"""FIPS 140-3 behaviour of the Node.js FIPS images (OpenSSL FIPS provider 3.1.2)."""
import subprocess

import pytest

# Throws inside the container print "REJECTED <code>", successes print "ALLOWED"
PROBE = """
const crypto = require('crypto');
function probe(fn) {
  try { fn(); console.log('ALLOWED'); } catch (e) { console.log('REJECTED ' + (e.code || e.message)); }
}
"""


def probe(node, expression):
    result = node(PROBE + f"probe(() => {{ {expression} }});")
    assert result.returncode == 0, result.stderr
    return result.stdout


# ==========================================
# FIPS mode
# ==========================================
def test_fips_mode_is_active(node):
    result = node("console.log(require('crypto').getFips())")
    assert result.stdout == "1", result.stderr


def test_fips_mode_cannot_be_disabled(node):
    output = probe(node, "crypto.setFips(false)")
    assert output.startswith("REJECTED ERR_CRYPTO_FIPS_FORCED"), output


def test_build_time_fips_check_passes(image):
    proc = subprocess.run(
        ["docker", "run", "--rm", "--entrypoint", "/usr/bin/node", image, "/usr/share/nodejs-fips/fips-check.js"],
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "FIPS check passed" in proc.stdout


# ==========================================
# Digests
# ==========================================
@pytest.mark.parametrize("algorithm", ["sha256", "sha384", "sha512", "sha3-256", "sha3-512"])
def test_approved_digest(node, algorithm):
    assert probe(node, f"crypto.createHash('{algorithm}').update('fips').digest()") == "ALLOWED"


@pytest.mark.parametrize("algorithm", ["md5", "md4", "ripemd160"])
def test_non_approved_digest_is_rejected(node, algorithm):
    assert probe(node, f"crypto.createHash('{algorithm}')").startswith("REJECTED")


# ==========================================
# Ciphers
# ==========================================
@pytest.mark.parametrize("cipher,key,iv", [("aes-256-gcm", 32, 12), ("aes-128-cbc", 16, 16), ("aes-256-ctr", 32, 16)])
def test_approved_cipher_round_trip(node, cipher, key, iv):
    script = f"""
const crypto = require('crypto');
const key = crypto.randomBytes({key}), iv = crypto.randomBytes({iv});
const enc = crypto.createCipheriv('{cipher}', key, iv);
const data = Buffer.concat([enc.update('fips round trip'), enc.final()]);
const dec = crypto.createDecipheriv('{cipher}', key, iv);
if ('{cipher}'.endsWith('gcm')) dec.setAuthTag(enc.getAuthTag());
console.log(Buffer.concat([dec.update(data), dec.final()]).toString());
"""
    result = node(script)
    assert result.stdout == "fips round trip", result.stderr


@pytest.mark.parametrize("cipher,key,iv", [("chacha20-poly1305", 32, 12), ("des-ede3-cbc", 24, 8), ("bf-cbc", 16, 8)])
def test_non_approved_cipher_is_rejected(node, cipher, key, iv):
    expression = f"crypto.createCipheriv('{cipher}', crypto.randomBytes({key}), crypto.randomBytes({iv}), {{ authTagLength: 16 }}).final()"
    assert probe(node, expression).startswith("REJECTED")


# ==========================================
# Public key cryptography
# ==========================================
@pytest.mark.parametrize("bits", [2048, 3072])
def test_rsa_approved_key_size(node, bits):
    assert probe(node, f"crypto.generateKeyPairSync('rsa', {{ modulusLength: {bits} }})") == "ALLOWED"


def test_rsa_1024_is_rejected(node):
    assert probe(node, "crypto.generateKeyPairSync('rsa', { modulusLength: 1024 })").startswith("REJECTED")


@pytest.mark.parametrize("curve", ["P-256", "P-384", "P-521"])
def test_nist_curve_signatures(node, curve):
    expression = (
        f"const {{ privateKey, publicKey }} = crypto.generateKeyPairSync('ec', {{ namedCurve: '{curve}' }});"
        "const sig = crypto.sign('sha256', Buffer.from('fips'), privateKey);"
        "if (!crypto.verify('sha256', Buffer.from('fips'), publicKey, sig)) throw new Error('verify failed');"
    )
    assert probe(node, expression) == "ALLOWED"


def test_non_nist_curve_is_rejected(node):
    assert probe(node, "crypto.generateKeyPairSync('ec', { namedCurve: 'secp256k1' })").startswith("REJECTED")


def test_ed25519_is_rejected(node):
    # EdDSA is not part of the OpenSSL 3.1.2 FIPS provider
    assert probe(node, "crypto.generateKeyPairSync('ed25519')").startswith("REJECTED")


# ==========================================
# MACs and key derivation
# ==========================================
def test_hmac_sha256(node):
    assert probe(node, "crypto.createHmac('sha256', crypto.randomBytes(32)).update('fips').digest()") == "ALLOWED"


def test_pbkdf2_sha256(node):
    assert probe(node, "crypto.pbkdf2Sync('a long enough password', crypto.randomBytes(16), 1000, 32, 'sha256')") == "ALLOWED"


def test_scrypt_is_rejected(node):
    assert probe(node, "crypto.scryptSync('password', crypto.randomBytes(16), 32)").startswith("REJECTED")


# ==========================================
# TLS
# ==========================================
def test_tls13_handshake_uses_approved_suite(node):
    script = """
const tls = require('tls'), fs = require('fs');
const server = tls.createServer({ key: fs.readFileSync('/fixtures/test-key.pem'), cert: fs.readFileSync('/fixtures/test-cert.pem') }, (s) => s.end('ok'));
server.listen(0, '127.0.0.1', () => {
  const socket = tls.connect({ port: server.address().port, host: '127.0.0.1', rejectUnauthorized: false }, () => {
    console.log(socket.getProtocol() + ' ' + socket.getCipher().name);
    socket.end(); server.close();
  });
  socket.on('error', (e) => { console.log('ERROR ' + e.message); server.close(); });
});
"""
    result = node(script, mount_fixtures=True)
    protocol, _, suite = result.stdout.partition(" ")
    assert protocol == "TLSv1.3", result.stdout + result.stderr
    assert "GCM" in suite and "CHACHA20" not in suite, suite


# ==========================================
# Image hardening
# ==========================================
def test_runs_as_non_root(node):
    assert node("console.log(process.getuid())").stdout == "1000"


def test_distroless_has_no_shell(image, flavor):
    if flavor != "prod":
        pytest.skip("only the distroless flavor is shell-less")
    for shell in ("/bin/sh", "/bin/bash", "/usr/bin/sh"):
        proc = subprocess.run(["docker", "run", "--rm", "--entrypoint", shell, image, "-c", "true"], capture_output=True, text=True)
        assert proc.returncode != 0, f"{shell} exists in the distroless image"


def test_npm_works_in_dev_image(image, flavor):
    if flavor != "dev":
        pytest.skip("npm only ships in the dev flavor")
    proc = subprocess.run(["docker", "run", "--rm", "--entrypoint", "npm", image, "--version"], capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
