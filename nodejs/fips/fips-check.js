'use strict';
// Verifies that Node.js runs with the OpenSSL FIPS provider enforced. Runs during
// the image build (a failure aborts the build) and can be run in any container:
//   node /usr/share/nodejs-fips/fips-check.js
const crypto = require('crypto');

const failures = [];

function throws(fn) {
  try {
    fn();
    return false;
  } catch {
    return true;
  }
}

function check(ok, message) {
  if (!ok) failures.push(message);
}

check(crypto.getFips() === 1, 'crypto.getFips() is not 1: the FIPS provider is not active');
check(throws(() => crypto.setFips(false)), 'crypto.setFips(false) is allowed: start node with --force-fips');
check(throws(() => crypto.createHash('md5')), 'MD5 is available: non-approved algorithms are not blocked');
check(throws(() => crypto.generateKeyPairSync('rsa', { modulusLength: 1024 })), 'RSA-1024 key generation is allowed');
check(!throws(() => crypto.createHash('sha256').update('fips').digest()), 'SHA-256 is unavailable');
check(!throws(() => {
  const cipher = crypto.createCipheriv('aes-256-gcm', crypto.randomBytes(32), crypto.randomBytes(12));
  cipher.update('fips');
  cipher.final();
}), 'AES-256-GCM is unavailable');

if (failures.length) {
  console.error('FIPS check FAILED:\n  - ' + failures.join('\n  - '));
  process.exit(1);
}
console.log(`FIPS check passed: Node.js ${process.version}, OpenSSL ${process.versions.openssl}, FIPS provider enforced`);
