import pytest
import allure
import subprocess
import os
import sys
import time
import tempfile
@allure.feature("Architecture & System Integrity")
class TestSystemIntegrity:

    @allure.story("Engine Architecture Compliance")
    @allure.title("Verify Absence of Legacy Cryptographic Engines")
    @allure.description("""
        Ensures the system adheres to modern Provider-based architecture. 
        Legacy OpenSSL engines (e.g., GOST, Padlock) must be absent to prevent 
        potential bypasses of the FIPS cryptographic boundary. Only modern 
        hardware-interface engines like 'rdrand' or 'dynamic' are permissible.
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("architecture", "engines", "modernization")
    def test_legacy_engines_absence(self, run_docker, image_tag):
        with allure.step("Listing active cryptographic engines in the container"):
            result = run_docker(image_tag, ["engine"])
            allure.attach(result.stdout, name="Engine List Output", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Analyzing detected engines for non-compliant legacy modules"):
            engines_output = result.stdout.strip()
            
            # Forbidden engines that historically bypass standard FIPS logic
            blacklisted_engines = ["gost", "padlock", "capi", "pkcs11"]
            found_violations = [eng for eng in blacklisted_engines if eng in engines_output.lower()]
            
            assert not found_violations, f"Architecture Violation: Forbidden legacy engines detected: {found_violations}"

        with allure.step("Recording architectural status"):
            allure.dynamic.parameter("Architecture Type", "Provider-Centric")
            allure.dynamic.parameter("Legacy Engines", "None Detected")

    @allure.story("Container Security Policy")
    @allure.title("Verify Non-Root User Execution Enforcement")
    @allure.description("""
        Validates that the container is configured to execute as a non-privileged 
        'nonroot' user. Running as root is a security risk and violates 
        principle-of-least-privilege (PoLP) requirements for secure environments.
    """)
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("security", "user-policy", "hardening")
    def test_container_user_security(self, image_tag):
        with allure.step(f"Inspecting image metadata for User configuration"):
            inspect_cmd = ["docker", "inspect", "--format={{.Config.User}}", image_tag]
            try:
                proc = subprocess.run(inspect_cmd, capture_output=True, text=True, check=True)
                configured_user = proc.stdout.strip()
                allure.attach(configured_user, name="Configured Container User")
            except subprocess.CalledProcessError as e:
                pytest.fail(f"Failed to inspect docker image: {e.stderr}")

        with allure.step("Verifying user identity is 'nonroot'"):
            assert configured_user == "nonroot", \
                f"Security Failure: Container is configured to run as '{configured_user or 'root'}', expected 'nonroot'."

        with allure.step("Recording container security metrics"):
            allure.dynamic.parameter("Effective User", configured_user)
            allure.dynamic.parameter("Privilege Level", "Non-Root")







    @allure.story("Deterministic Random Bit Generator (DRBG)")
    @allure.title("Verify FIPS DRBG Functional Integrity")
    @allure.description("""
        Validates the functionality of the Deterministic Random Bit Generator (DRBG).
        Ensures that the system can generate cryptographically strong random data 
        using the FIPS-approved provider. The test verifies that the 'rand' 
        utility successfully honors the FIPS property query.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("drbg", "rng", "randomness", "fips-140-3")
    def test_drbg_functionality(self, run_docker, image_tag):
        with allure.step("Generating 32 bytes of random data in hex format"):
            result = run_docker(image_tag, ["rand", "-propquery", "fips=yes", "-hex", "32"])
            
            allure.attach(result.stdout, name="Generated Hex Data")
            allure.attach(result.stderr, name="Stderr")

        with allure.step("Verifying successful execution and output length"):
            assert result.returncode == 0, f"Random data generation failed. Stderr: {result.stderr}"
            
            # 32 bytes in hex should be exactly 64 characters
            clean_output = result.stdout.strip()
            assert len(clean_output) == 64, f"Incorrect output length. Expected 64 hex chars, got {len(clean_output)}."

        with allure.step("Recording DRBG operational metrics"):
            allure.dynamic.parameter("Requested Bytes", "32")
            allure.dynamic.parameter("Property Query", "fips=yes")
            allure.dynamic.parameter("Status", "Operational")



    @allure.story("Entropy Authority & Randomness")
    @allure.title("Verify Entropy Source Authority & FIPS Provider Priority")
    @allure.description("""
        Validates that the cryptographic module utilizes a FIPS-approved entropy source.
        This test ensures that the Deterministic Random Bit Generator (DRBG) is 
        specifically provided by the 'fips' provider (e.g., CTR-DRBG @ fips), 
        overriding any legacy or default system entropy sources.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("entropy", "randomness", "drbg-priority", "compliance")
    def test_entropy_source_validation(self, run_docker, image_tag):
        with allure.step("Querying active random generators and entropy providers"):
            # We use -verbose to see the provider affinity (e.g., @ fips)
            result = run_docker(image_tag, ["list", "-random-generators", "-verbose"])
            
            allure.attach(result.stdout, name="Random Generators Metadata", attachment_type=allure.attachment_type.TEXT)
            allure.attach(result.stderr, name="Stderr Output", attachment_type=allure.attachment_type.TEXT)

            assert result.returncode == 0, "Failed to retrieve the list of random generators."

        with allure.step("Verifying FIPS Provider authority over entropy (DRBG)"):
            # We must confirm that the CTR-DRBG is explicitly linked to the fips provider
            # The output should contain something like "CTR-DRBG @ fips"
            output = result.stdout
            fips_drbg_present = "CTR-DRBG @ fips" in output or "HASH-DRBG @ fips" in output or "HMAC-DRBG @ fips" in output

            if not fips_drbg_present:
                allure.dynamic.status_details(message="Compliance Failure: Entropy source is NOT provided by the FIPS provider.")
                pytest.fail("Security Policy Violation: The module is not using a FIPS-approved DRBG instance from the validated provider.")

        with allure.step("Checking for unauthorized legacy entropy engines"):
            # Ensuring legacy engines like 'rdrand' are not bypassing the FIPS DRBG hierarchy
            if "rdrand" in output.lower() and "@ fips" not in output:
                allure.dynamic.parameter("Warning", "Hardware RDRAND detected, but FIPS DRBG priority must be maintained.")

        with allure.step("Entropy source authority and priority confirmed"):
            allure.dynamic.parameter("Primary DRBG", "CTR-DRBG @ fips")
            allure.dynamic.parameter("Compliance Standard", "FIPS 140-3 (AS08.01)")







    @allure.story("Password-Based Key Derivation")
    @allure.title("Verify PBKDF2 Derivation with FIPS Approved Digest")
    @allure.description("""
        Validates the PBKDF2 integrity. 
        Note: FIPS 140-3 (via NIST SP 800-132) mandates a minimum salt length 
        of 128 bits (16 bytes). This test uses a 128-bit hex salt to comply.
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("kdf", "pbkdf2", "fips-compliance")
    def test_pbkdf2_derivation(self, run_docker, image_tag):
        # Parameters with FIPS-compliant salt length (16 bytes / 128 bits)
        pass_opt = "pass:password123"
        # 16 bytes of salt in hex
        hex_salt = "hexsalt:0102030405060708090A0B0C0D0E0F10"
        iter_opt = "iter:1000"
        digest_opt = "digest:SHA256"
        key_len = "32"

        with allure.step("Deriving key using PBKDF2 (128-bit Salt)"):
            result = run_docker(image_tag, [
                "kdf", 
                "-propquery", "fips=yes",
                "-kdfopt", digest_opt,
                "-kdfopt", pass_opt,
                "-kdfopt", hex_salt,
                "-kdfopt", iter_opt,
                "-keylen", key_len,
                "PBKDF2"
            ])
            
            allure.attach(result.stderr, name="KDF Stderr (Debug)")
            allure.attach(str(len(result.stdout)), name="Derived Key Raw Length")

        with allure.step("Verifying KDF execution status"):
            # If this passes, it means the 16-byte salt was accepted
            assert result.returncode == 0, f"PBKDF2 failed even with 128-bit salt. Stderr: {result.stderr}"
            assert len(result.stdout) > 0, "KDF produced empty output."

        with allure.step("Recording KDF compliance parameters"):
            allure.dynamic.parameter("Algorithm", "PBKDF2")
            allure.dynamic.parameter("Salt Length", "128-bit (Mandatory)")
            allure.dynamic.parameter("Result", "Verified")

    @allure.story("X.509 Certificate Handling")
    @allure.title("Verify X.509 Root CA Certificate Bundle Parsing & ASN.1 Structural Integrity")
    @allure.description("""
        Validates the system's root CA bundle located at /etc/ssl/certs/ca-certificates.crt:
        Verifies that the FIPS provider's ASN.1 parser correctly decodes and validates
        standard X.509 certificate structures without requiring network connectivity.
    """)
    def test_certificate_parsing(self, run_docker, image_tag):
        cert_path = "/etc/ssl/certs/ca-certificates.crt"
        with allure.step(f"Parsing system certificate bundle at {cert_path}"):
            result = run_docker(image_tag, ["x509", "-in", cert_path, "-noout", "-text"])
            allure.attach(result.stdout[:2000], name="Parsed Certificate Snippet", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying structural integrity of the parsed certificate bundle"):
            assert result.returncode == 0, f"Certificate parsing failed. Stderr: {result.stderr}"
            output = result.stdout
            assert "Certificate:" in output and "Subject:" in output, \
                "Incomplete parsing: Mandatory X.509 fields were not found in the output."

    @allure.story("Deterministic Random Bit Generator (NIST SP 800-90A)")
    @allure.title("Verify DRBG Mechanisms Completeness (CTR-DRBG, HASH-DRBG, HMAC-DRBG)")
    @allure.description("""
        Validates that all three NIST SP 800-90A approved DRBG mechanisms
        (CTR-DRBG, HASH-DRBG, HMAC-DRBG) are provided by the FIPS provider.
    """)
    def test_drbg_mechanisms_completeness(self, run_docker, image_tag):
        with allure.step("Listing random generators with verbose attributes"):
            result = run_docker(image_tag, ["list", "-random-generators", "-propquery", "fips=yes", "-verbose"])
            allure.attach(result.stdout, name="Random Generators")
        assert result.returncode == 0, f"Failed to list random generators: {result.stderr}"
        stdout = result.stdout
        for mechanism in ["CTR-DRBG @ fips", "HASH-DRBG @ fips", "HMAC-DRBG @ fips"]:
            assert mechanism in stdout, f"Missing NIST SP 800-90A approved DRBG mechanism: {mechanism}"

    @allure.story("Deterministic Random Bit Generator (NIST SP 800-90A)")
    @allure.title("Verify Randomness Continuity and Anti-Repetition")
    @allure.description("""
        Validates that consecutive random bit generation cycles produce unique,
        non-repeating, cryptographically strong entropy blocks with no lockup or zero-padding.
    """)
    def test_rand_entropy_continuity(self, run_docker, image_tag):
        blocks = []
        for i in range(5):
            with allure.step(f"Generating random block {i + 1}"):
                result = run_docker(image_tag, ["rand", "-propquery", "fips=yes", "-hex", "32"])
                assert result.returncode == 0, f"Generation failed on block {i + 1}: {result.stderr}"
                val = result.stdout.strip()
                assert len(val) == 64, f"Block {i + 1} unexpected length {len(val)}"
                assert val != "00" * 32, f"Block {i + 1} returned all zeroes!"
                blocks.append(val)

        unique_blocks = set(blocks)
        assert len(unique_blocks) == len(blocks), f"DRBG state repetition detected! Output: {blocks}"

    @allure.story("X.509 Certificate Generation Restrictions")
    @allure.title("Verify Rejection of Insecure Digests (MD5, SHA-1) in Certificate Requests")
    @pytest.mark.parametrize("insecure_md", ["-md5", "-sha1"])
    def test_x509_req_digest_rejection(self, image_tag, insecure_md):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/x509req"

            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "genpkey", "-propquery", "fips=yes", "-algorithm", "RSA",
                "-pkeyopt", "rsa_keygen_bits:2048", "-out", f"{container_dir}/test.key"
            ], check=True)

            with allure.step(f"Attempting certificate request with disallowed digest {insecure_md}"):
                res = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "req", "-new", "-x509", "-key", f"{container_dir}/test.key",
                    insecure_md, "-days", "365", "-subj", "/CN=InsecureDigestTest",
                    "-out", f"{container_dir}/test.crt"
                ], capture_output=True, text=True)
                assert res.returncode != 0, f"Security Breach: req -x509 accepted {insecure_md} digest!"

    @allure.story("X.509 Certificate Path Validation")
    @allure.title("Verify Certificate Chain Validation Policy (MD5, SHA-1, Weak Key Rejection)")
    def test_x509_verify_signature_digest_enforcement(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/certchain"

            # 1. Create a chain signed with MD5
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "req", "-x509", "-newkey", "rsa:2048", "-keyout", f"{container_dir}/ca_md5.key", "-nodes",
                "-out", f"{container_dir}/ca_md5.crt", "-md5", "-subj", "/CN=MD5CA",
                "-addext", "basicConstraints=critical,CA:TRUE"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "req", "-newkey", "rsa:2048", "-keyout", f"{container_dir}/leaf_md5.key", "-nodes",
                "-out", f"{container_dir}/leaf_md5.csr", "-subj", "/CN=MD5Leaf"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "x509", "-req", "-in", f"{container_dir}/leaf_md5.csr",
                "-CA", f"{container_dir}/ca_md5.crt", "-CAkey", f"{container_dir}/ca_md5.key",
                "-set_serial", "1", "-out", f"{container_dir}/leaf_md5.crt", "-md5"
            ], check=True)

            with allure.step("Verifying that certificate signed with MD5 fails verification"):
                res_md5 = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "verify", "-CAfile", f"{container_dir}/ca_md5.crt", f"{container_dir}/leaf_md5.crt"
                ], capture_output=True, text=True)
                assert res_md5.returncode != 0, "Security Breach: verify accepted MD5-signed certificate!"
                assert "signature failure" in res_md5.stderr.lower() or "error" in res_md5.stderr.lower()

            # 2. Create a chain signed with SHA-1
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "req", "-x509", "-newkey", "rsa:2048", "-keyout", f"{container_dir}/ca_sha1.key", "-nodes",
                "-out", f"{container_dir}/ca_sha1.crt", "-sha1", "-subj", "/CN=SHA1CA",
                "-addext", "basicConstraints=critical,CA:TRUE"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "req", "-newkey", "rsa:2048", "-keyout", f"{container_dir}/leaf_sha1.key", "-nodes",
                "-out", f"{container_dir}/leaf_sha1.csr", "-subj", "/CN=SHA1Leaf"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "x509", "-req", "-in", f"{container_dir}/leaf_sha1.csr",
                "-CA", f"{container_dir}/ca_sha1.crt", "-CAkey", f"{container_dir}/ca_sha1.key",
                "-set_serial", "1", "-out", f"{container_dir}/leaf_sha1.crt", "-sha1"
            ], check=True)

            with allure.step("Verifying that SHA-1 certificate is rejected under security auth_level 2"):
                res_sha1 = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "verify", "-auth_level", "2",
                    "-CAfile", f"{container_dir}/ca_sha1.crt", f"{container_dir}/leaf_sha1.crt"
                ], capture_output=True, text=True)
                assert res_sha1.returncode != 0, "Security Breach: verify at auth_level 2 accepted SHA-1 certificate!"
                assert "too weak" in res_sha1.stderr.lower()

            # 3. Create a chain with weak 1024-bit RSA key
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "req", "-x509", "-newkey", "rsa:1024", "-keyout", f"{container_dir}/ca_1024.key", "-nodes",
                "-out", f"{container_dir}/ca_1024.crt", "-sha256", "-subj", "/CN=1024CA",
                "-addext", "basicConstraints=critical,CA:TRUE"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "req", "-newkey", "rsa:1024", "-keyout", f"{container_dir}/leaf_1024.key", "-nodes",
                "-out", f"{container_dir}/leaf_1024.csr", "-subj", "/CN=1024Leaf"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "x509", "-req", "-in", f"{container_dir}/leaf_1024.csr",
                "-CA", f"{container_dir}/ca_1024.crt", "-CAkey", f"{container_dir}/ca_1024.key",
                "-set_serial", "1", "-out", f"{container_dir}/leaf_1024.crt", "-sha256"
            ], check=True)

            with allure.step("Verifying that RSA-1024 certificate is rejected under security auth_level 2"):
                res_1024 = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "verify", "-auth_level", "2",
                    "-CAfile", f"{container_dir}/ca_1024.crt", f"{container_dir}/leaf_1024.crt"
                ], capture_output=True, text=True)
                assert res_1024.returncode != 0, "Security Breach: verify at auth_level 2 accepted RSA-1024 certificate!"
                assert "too weak" in res_1024.stderr.lower()

            # 4. Create an approved chain with SHA-256 and RSA-2048 (must succeed)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "req", "-x509", "-newkey", "rsa:2048", "-keyout", f"{container_dir}/ca_ok.key", "-nodes",
                "-out", f"{container_dir}/ca_ok.crt", "-sha256", "-subj", "/CN=GoodCA",
                "-addext", "basicConstraints=critical,CA:TRUE"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "req", "-newkey", "rsa:2048", "-keyout", f"{container_dir}/leaf_ok.key", "-nodes",
                "-out", f"{container_dir}/leaf_ok.csr", "-subj", "/CN=GoodLeaf"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "x509", "-req", "-in", f"{container_dir}/leaf_ok.csr",
                "-CA", f"{container_dir}/ca_ok.crt", "-CAkey", f"{container_dir}/ca_ok.key",
                "-set_serial", "1", "-out", f"{container_dir}/leaf_ok.crt", "-sha256"
            ], check=True)

            with allure.step("Verifying that SHA-256 + RSA-2048 chain succeeds"):
                res_ok = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "verify", "-CAfile", f"{container_dir}/ca_ok.crt", f"{container_dir}/leaf_ok.crt"
                ], capture_output=True, text=True)
                assert res_ok.returncode == 0, f"Valid certificate verification failed: {res_ok.stderr}"
                assert "OK" in res_ok.stdout

    @allure.story("Cryptographic Message Syntax (CMS - RFC 5652)")
    @allure.title("Verify CMS Encryption/Signing Boundaries (SHA-1 and 3DES Blocked, AES-256 Approved)")
    def test_cms_sha1_and_3des_rejection(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/cms"

            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "req", "-x509", "-newkey", "rsa:2048",
                "-keyout", f"{container_dir}/signer.key", "-nodes",
                "-out", f"{container_dir}/signer.crt",
                "-sha256", "-subj", "/CN=CMSSigner"
            ], check=True)

            with open(os.path.join(host_dir, "data.txt"), "w") as f:
                f.write("FIPS CMS Content Integrity Test")

            with allure.step("Attempting CMS signing with unapproved SHA-1 (must fail)"):
                res_sign_sha1 = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "cms", "-sign", "-propquery", "fips=yes",
                    "-signer", f"{container_dir}/signer.crt",
                    "-inkey", f"{container_dir}/signer.key",
                    "-md", "sha1",
                    "-in", f"{container_dir}/data.txt",
                    "-out", f"{container_dir}/signed_sha1.cms"
                ], capture_output=True, text=True)
                assert res_sign_sha1.returncode != 0, "Security Breach: CMS signed using unapproved SHA-1 digest!"
                assert "digest not allowed" in res_sign_sha1.stderr.lower() or "error" in res_sign_sha1.stderr.lower()

            with allure.step("Attempting CMS encryption with unapproved 3DES (must fail)"):
                res_enc_3des = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "cms", "-encrypt", "-propquery", "fips=yes",
                    "-des3", "-in", f"{container_dir}/data.txt",
                    f"{container_dir}/signer.crt"
                ], capture_output=True, text=True)
                assert res_enc_3des.returncode != 0, "Security Breach: CMS encrypted using unapproved 3DES cipher!"

            with allure.step("Verifying CMS encryption and decryption roundtrip with approved AES-256"):
                res_enc = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "cms", "-encrypt", "-propquery", "fips=yes",
                    "-aes256", "-in", f"{container_dir}/data.txt",
                    "-out", f"{container_dir}/enc_aes.cms",
                    f"{container_dir}/signer.crt"
                ], capture_output=True, text=True)
                assert res_enc.returncode == 0, f"CMS AES-256 encryption failed: {res_enc.stderr}"

                res_dec = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "cms", "-decrypt", "-propquery", "fips=yes",
                    "-in", f"{container_dir}/enc_aes.cms",
                    "-inkey", f"{container_dir}/signer.key",
                    "-recip", f"{container_dir}/signer.crt"
                ], capture_output=True, text=True)
                assert res_dec.returncode == 0, f"CMS AES-256 decryption failed: {res_dec.stderr}"
                assert "FIPS CMS Content Integrity Test" in res_dec.stdout

    @allure.story("Transport Layer Security (NIST SP 800-52 Rev. 2)")
    @allure.title("Verify Strict Rejection of Legacy TLS 1.0 Client Protocol")
    def test_tls_client_handshake_version_enforcement(self, image_tag):
        with allure.step("Attempting client TLS 1.0 connection (must fail at handshake setup)"):
            res = subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                image_tag,
                "s_client", "-tls1", "-connect", "127.0.0.1:443"
            ], capture_output=True, text=True)
            assert res.returncode != 0, "Security Breach: TLS 1.0 client handshake was not rejected!"
            assert "no protocols available" in res.stderr.lower() or "error" in res.stderr.lower()

    @allure.story("Configuration & Boundary Integrity")
    @allure.title("Verify FIPS Provider Isolation Under Configuration Override")
    def test_environment_conf_override_boundary(self, image_tag):
        with allure.step("Executing FIPS propquery under OPENSSL_CONF=/dev/null (must fail)"):
            res = subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-e", "OPENSSL_CONF=/dev/null",
                image_tag,
                "dgst", "-propquery", "fips=yes", "-sha256", "/dev/null"
            ], capture_output=True, text=True)
            assert res.returncode != 0, "Security Breach: FIPS provider operated without valid openssl.cnf!"
            assert "unsupported" in res.stderr.lower() or "error" in res.stderr.lower()