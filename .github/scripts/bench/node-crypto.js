'use strict';
// Crypto throughput of a Node.js image; prints one JSON array. Mounted read-only into the container.
const crypto = require('crypto');

const SECONDS = Number(process.env.BENCH_SECONDS || 1);
const data = crypto.randomBytes(16384);
const key = crypto.randomBytes(32);
const ec = crypto.generateKeyPairSync('ec', { namedCurve: 'P-256' });
const rsa = crypto.generateKeyPairSync('rsa', { modulusLength: 2048 });
const ecSig = crypto.sign('sha256', data, ec.privateKey);
const rsaSig = crypto.sign('sha256', data, rsa.privateKey);

// Runs fn repeatedly for SECONDS and returns MB/s (when bytes is given) or operations per second
function measure(fn, bytes) {
  const start = process.hrtime.bigint();
  const end = start + BigInt(Math.round(SECONDS * 1e9));
  let count = 0;
  while (process.hrtime.bigint() < end) {
    fn();
    count++;
  }
  const elapsed = Number(process.hrtime.bigint() - start) / 1e9;
  return bytes ? (count * bytes) / elapsed / 1e6 : count / elapsed;
}

const results = [
  ['SHA-256', 'MB/s', () => crypto.createHash('sha256').update(data).digest(), data.length],
  ['SHA-512', 'MB/s', () => crypto.createHash('sha512').update(data).digest(), data.length],
  ['HMAC-SHA256', 'MB/s', () => crypto.createHmac('sha256', key).update(data).digest(), data.length],
  ['AES-256-GCM encrypt', 'MB/s', () => {
    const cipher = crypto.createCipheriv('aes-256-gcm', key, crypto.randomBytes(12));
    cipher.update(data);
    cipher.final();
  }, data.length],
  ['ECDSA P-256 sign', 'ops/s', () => crypto.sign('sha256', data, ec.privateKey)],
  ['ECDSA P-256 verify', 'ops/s', () => crypto.verify('sha256', data, ec.publicKey, ecSig)],
  ['RSA-2048 sign', 'ops/s', () => crypto.sign('sha256', data, rsa.privateKey)],
  ['RSA-2048 verify', 'ops/s', () => crypto.verify('sha256', data, rsa.publicKey, rsaSig)],
].map(([name, metric, fn, bytes]) => ({ name, metric, value: measure(fn, bytes) }));

console.log(JSON.stringify(results));
