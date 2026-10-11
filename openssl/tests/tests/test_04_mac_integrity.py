import os
import tempfile
import subprocess
import pytest
import allure

@allure.feature("Message Authentication Codes (MAC)")
class TestHMACBoundaries:

    @pytest.mark.xfail(strict=True, reason="Known limitation of the certified OpenSSL FIPS provider 3.1.2: minimum HMAC key length (hmac-key-check) is only enforced from the 3.4 provider; key length is an operator requirement")
    @allure.story("HMAC Key Strength Enforcement")
    @allure.title("Verify Rejection of Weak Keys across SHA-2 Family")
    @allure.description("""
        Performs an exhaustive sweep across the SHA-2 digest family.
        Forces the use of the FIPS provider via property query.
        Validates that a sub-standard 8-bit key is rejected to meet FIPS 140-3 standards.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("hmac", "sha2", "key-length", "strict-fips")
    def test_hmac_sha2_key_length_exhaustive(self, run_docker, image_tag):
        sha2_variants = ["SHA224", "SHA256", "SHA384", "SHA512"]
        failed_variants = []

        for variant in sha2_variants:
            with allure.step(f"Testing HMAC-{variant} with 8-bit key (Strict FIPS)"):
                # أضفنا -propquery fips=yes لإجبار النظام على استخدام معايير FIPS فقط
                result = run_docker(image_tag, [
                    "mac", "-propquery", "fips=yes", 
                    "-digest", variant, 
                    "-macopt", "hexkey:01", "HMAC"
                ])
                
                if result.returncode == 0:
                    failed_variants.append(variant)
                
                allure.attach(result.stderr, name=f"{variant} Error Log")

        with allure.step("Analyzing sweep results"):
            assert not failed_variants, f"Compliance Failure: FIPS provider allowed weak 8-bit key for: {failed_variants}"

    @pytest.mark.xfail(strict=True, reason="Known limitation of the certified OpenSSL FIPS provider 3.1.2: minimum HMAC key length (hmac-key-check) is only enforced from the 3.4 provider; key length is an operator requirement")
    @allure.story("HMAC Key Strength Enforcement")
    @allure.title("Verify Precise 112-bit Security Boundary")
    @allure.description("""
        Validates the exact transition point for HMAC security strength.
        Ensures that 104-bit keys are rejected and 112-bit keys are accepted 
        under strict FIPS property queries.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("hmac", "nist-threshold", "boundary-testing")
    def test_hmac_112bit_security_boundary(self, run_docker, image_tag):
        key_104_bit = "0102030405060708090A0B0C0D"
        key_112_bit = "0102030405060708090A0B0C0D0E"

        with allure.step("Testing sub-threshold key (104-bit) with FIPS query"):
            result_104 = run_docker(image_tag, [
                "mac", "-propquery", "fips=yes", 
                "-digest", "SHA256", 
                "-macopt", f"hexkey:{key_104_bit}", "HMAC"
            ])
            assert result_104.returncode != 0, "Compliance Failure: System accepted 104-bit key under FIPS query."

        with allure.step("Testing minimum compliant key (112-bit) with FIPS query"):
            result_112 = run_docker(image_tag, [
                "mac", "-propquery", "fips=yes", 
                "-digest", "SHA256", 
                "-macopt", f"hexkey:{key_112_bit}", "HMAC"
            ])
            assert result_112.returncode == 0, f"Functional Failure: 112-bit key rejected. Stderr: {result_112.stderr}"

@allure.feature("Message Authentication Codes (MAC)")
class TestModernMACs:

    @allure.story("MAC Policy Consistency")
    @allure.title("Verify CMAC-AES Key Strength Enforcement")
    @allure.description("""
        Validates the enforcement of cryptographic strength for Block Cipher-based MACs (CMAC).
        The system must reject CMAC-AES operations if the provided key does not meet 
        the mandatory AES bit-length requirements (128, 192, or 256 bits).
        Tests using an invalid 64-bit (8-byte) key.
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("mac", "cmac", "aes-policy", "key-validation")
    def test_cmac_aes_key_policy(self, run_docker, image_tag):
        invalid_key = "0102030405060708"
        
        with allure.step("Attempting CMAC-AES with 64-bit key (Strict FIPS)"):
            result = run_docker(image_tag, [
                "mac", "-propquery", "fips=yes",
                "-cipher", "AES-128-CBC", 
                "-macopt", f"hexkey:{invalid_key}", "CMAC"
            ])
            allure.attach(result.stderr, name="CMAC Rejection Log", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying mandatory rejection of invalid key length"):
            assert result.returncode != 0, "Compliance Failure: CMAC accepted an invalid 64-bit AES key."

    @allure.story("Modern MAC Enforcement")
    @allure.title("Verify KMAC-SHA3 Security Strength")
    @allure.description("""
        Validates the security policy for Keccak-based Message Authentication Codes (KMAC).
        In accordance with NIST SP 800-185, KMAC must enforce a minimum security strength.
        This test ensures that the FIPS provider rejects KMAC-128 operations 
        using a weak sub-112 bit (32-bit) key.
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("mac", "kmac", "sha3", "nist-sp-800-185")
    def test_kmac_sha3_strength(self, run_docker, image_tag):
        weak_key = "01020304"
        
        with allure.step("Attempting KMAC-128 with 32-bit key (Strict FIPS)"):
            result = run_docker(image_tag, [
                "mac", "-propquery", "fips=yes",
                "-digest", "KMAC128", 
                "-macopt", f"hexkey:{weak_key}", "KMAC"
            ])
            allure.attach(result.stderr, name="KMAC Error Log", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying rejection of weak SHA3-based MAC key"):
            assert result.returncode != 0, "Compliance Failure: KMAC accepted a weak 32-bit key under FIPS query."

    @allure.story("GMAC Authentication")
    @allure.title("Verify GMAC-AES Functional Integrity (NIST SP 800-38D)")
    @allure.description("""
        Validates GMAC (Galois Message Authentication Code) with AES-128 and AES-256 ciphers.
    """)
    @pytest.mark.parametrize("cipher,key_hex", [
        ("AES-128-GCM", "01" * 16),
        ("AES-256-GCM", "01" * 32)
    ])
    def test_gmac_aes_availability(self, run_docker, image_tag, cipher, key_hex):
        iv_hex = "02" * 12
        with allure.step(f"Calculating GMAC with {cipher}"):
            result = run_docker(image_tag, [
                "mac", "-propquery", "fips=yes",
                "-cipher", cipher,
                "-macopt", f"hexkey:{key_hex}",
                "-macopt", f"hexiv:{iv_hex}",
                "GMAC"
            ], input_data=b"FIPS-GMAC-INTEGRITY-PAYLOAD\n")
            allure.attach(result.stdout, name=f"{cipher} GMAC Output")

        assert result.returncode == 0, f"GMAC calculation failed for {cipher}: {result.stderr}"
        assert len(result.stdout.strip()) == 32, f"GMAC tag length expected 32 hex chars, got {result.stdout.strip()}"

    @allure.story("GMAC Authentication")
    @allure.title("Verify GMAC Rejection of Non-Approved Ciphers")
    @allure.description("""
        Ensures that GMAC rejects non-GCM or non-approved ciphers (e.g., DES-EDE3-CBC).
    """)
    def test_gmac_unapproved_cipher_rejection(self, run_docker, image_tag):
        with allure.step("Attempting GMAC with DES-EDE3-CBC"):
            result = run_docker(image_tag, [
                "mac", "-propquery", "fips=yes",
                "-cipher", "DES-EDE3-CBC",
                "-macopt", "hexkey:0102030405060708090a0b0c0d0e0f101112131415161718",
                "-macopt", "hexiv:0102030405060708",
                "GMAC"
            ])
        assert result.returncode != 0, "Security Breach: GMAC accepted non-approved DES cipher!"

    @allure.story("HMAC Digest Boundaries")
    @allure.title("Verify FIPS-Approved Digests with HMAC")
    @allure.description("""
        Validates HMAC computation using approved SHA-2 and SHA-3 family digests.
    """)
    @pytest.mark.parametrize("digest_name", [
        "SHA224", "SHA256", "SHA384", "SHA512",
        "SHA3-224", "SHA3-256", "SHA3-384", "SHA3-512"
    ])
    def test_hmac_approved_digests(self, run_docker, image_tag, digest_name):
        compliant_key = "0102030405060708090A0B0C0D0E"  # 112 bits
        with allure.step(f"Calculating HMAC-{digest_name}"):
            result = run_docker(image_tag, [
                "mac", "-propquery", "fips=yes",
                "-digest", digest_name,
                "-macopt", f"hexkey:{compliant_key}",
                "HMAC"
            ], input_data=b"HMAC-TEST-MESSAGE\n")
        assert result.returncode == 0, f"HMAC-{digest_name} failed: {result.stderr}"
        assert len(result.stdout.strip()) > 0

    @allure.story("HMAC Digest Boundaries")
    @allure.title("Verify Rejection of Insecure Digests for HMAC")
    @allure.description("""
        Validates that insecure digests (MD5, MD4, RIPEMD160) are rejected when used with HMAC.
    """)
    @pytest.mark.parametrize("insecure_digest", ["MD5", "MD4", "RIPEMD160"])
    def test_hmac_insecure_digest_rejection(self, run_docker, image_tag, insecure_digest):
        with allure.step(f"Attempting HMAC with unapproved digest {insecure_digest}"):
            result = run_docker(image_tag, [
                "mac", "-propquery", "fips=yes",
                "-digest", insecure_digest,
                "-macopt", "hexkey:0102030405060708090A0B0C0D0E",
                "HMAC"
            ])
        assert result.returncode != 0, f"Security Breach: HMAC accepted insecure digest {insecure_digest}!"




    @allure.story("NIST SP 800-108 KDF Enforcement")
    @allure.title("Verify SP 800-108 Counter Mode KDF Integrity")
    @allure.description("""
        Validates KBKDF in Counter Mode. 
        Note: KBKDF requires an explicit MAC algorithm (HMAC or CMAC).
        This test uses HMAC-SHA256 as the underlying PRF.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("kdf", "kbkdf", "counter-mode", "debug")
    def test_sp800_108_counter_kdf(self, run_docker, image_tag):
        # Step 1: Debug - Check kdf help if needed
        with allure.step("Debugging: Checking KDF tool help"):
            help_res = run_docker(image_tag, ["kdf", "-help"])
            allure.attach(help_res.stderr, name="KDF Help Output")

        with allure.step("Executing KBKDF Counter Mode (HMAC-SHA256)"):
            # Correct parameters: must specify mac:HMAC and digest:SHA256
            result = run_docker(image_tag, [
                "kdf", 
                "-propquery", "fips=yes",
                "-kdfopt", "mac:HMAC",
                "-kdfopt", "digest:SHA256", 
                "-kdfopt", "hexkey:0102030405060708090A0B0C0D0E0F10", 
                "-kdfopt", "mode:COUNTER",
                "-keylen", "16", 
                "KBKDF"
            ])
            
            allure.attach(result.stdout, name="Derived Key Raw")
            allure.attach(result.stderr, name="Stderr Log")

        with allure.step("Verifying successful execution"):
            assert result.returncode == 0, f"KBKDF Counter Mode failed. Stderr: {result.stderr}"
            assert len(result.stdout) > 0

    @allure.story("NIST SP 800-108 KDF Enforcement")
    @allure.title("Verify SP 800-108 Feedback Mode KDF Integrity")
    @allure.description("""
        Validates KBKDF in Feedback Mode using HMAC-SHA256 as the PRF.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("kdf", "kbkdf", "feedback-mode")
    def test_sp800_108_feedback_kdf(self, run_docker, image_tag):
        with allure.step("Executing KBKDF Feedback Mode (HMAC-SHA256)"):
            result = run_docker(image_tag, [
                "kdf", 
                "-propquery", "fips=yes",
                "-kdfopt", "mac:HMAC",
                "-kdfopt", "digest:SHA256", 
                "-kdfopt", "hexkey:0102030405060708090A0B0C0D0E0F10", 
                "-kdfopt", "mode:FEEDBACK",
                "-keylen", "16", 
                "KBKDF"
            ])
            
            allure.attach(result.stdout, name="Derived Key Raw")
            allure.attach(result.stderr, name="Stderr Log")

        with allure.step("Verifying successful execution"):
            assert result.returncode == 0, f"KBKDF Feedback Mode failed. Stderr: {result.stderr}"
            assert len(result.stdout) > 0

    @allure.story("NIST SP 800-56C KDF Enforcement")
    @allure.title("Verify HKDF and SSKDF Key Derivation Integrity")
    @allure.description("""
        Validates HKDF (RFC 5869 / SP 800-56C) and Single-Step KDF (SSKDF)
        using approved SHA-256 digest, and confirms strict rejection of unapproved MD5 digest.
    """)
    def test_hkdf_and_sskdf_integrity(self, run_docker, image_tag):
        with allure.step("Validating HKDF with approved SHA-256"):
            res_hkdf = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "hexsalt:0102030405060708",
                "-keylen", "16", "HKDF"
            ])
            assert res_hkdf.returncode == 0, f"HKDF SHA-256 failed: {res_hkdf.stderr}"
            assert len(res_hkdf.stdout.strip()) > 0

        with allure.step("Validating HKDF rejection of unapproved MD5"):
            res_hkdf_md5 = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:MD5",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "hexsalt:0102030405060708",
                "-keylen", "16", "HKDF"
            ])
            assert res_hkdf_md5.returncode != 0, "Security Breach: HKDF accepted unapproved MD5 digest!"

        with allure.step("Validating SSKDF with approved SHA-256"):
            res_sskdf = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-keylen", "16", "SSKDF"
            ])
            assert res_sskdf.returncode == 0, f"SSKDF SHA-256 failed: {res_sskdf.stderr}"
            assert len(res_sskdf.stdout.strip()) > 0

        with allure.step("Validating SSKDF rejection of unapproved MD5"):
            res_sskdf_md5 = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:MD5",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-keylen", "16", "SSKDF"
            ])
            assert res_sskdf_md5.returncode != 0, "Security Breach: SSKDF accepted unapproved MD5 digest!"

    @allure.story("NIST SP 800-185 KMAC Integrity")
    @allure.title("Verify KMAC-128 and KMAC-256 Functional Integrity (NIST SP 800-185)")
    @allure.description("""
        Validates KMAC-128 and KMAC-256 execution with compliant key lengths and output sizes.
        Ensures SHA-3 based message authentication codes operate properly within the FIPS boundary.
    """)
    @pytest.mark.parametrize("kmac_algo,key_hex,out_len", [
        ("KMAC128", "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f", 32),
        ("KMAC256", "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f", 64)
    ])
    def test_kmac_nist_sp800_185(self, run_docker, image_tag, kmac_algo, key_hex, out_len):
        with allure.step(f"Calculating {kmac_algo} with {out_len}-byte output"):
            result = run_docker(image_tag, [
                "mac", "-propquery", "fips=yes",
                "-macopt", f"hexkey:{key_hex}",
                "-macopt", f"size:{out_len}",
                kmac_algo
            ], input_data=b"NIST-KMAC-MESSAGE-INTEGRITY-PAYLOAD\n")
            allure.attach(result.stdout, name=f"{kmac_algo} Output")

        assert result.returncode == 0, f"{kmac_algo} failed: {result.stderr}"
        tag_hex = result.stdout.strip()
        assert len(tag_hex) == out_len * 2, f"Expected {out_len * 2} hex chars, got {len(tag_hex)}"

    @allure.story("Unapproved MAC Algorithms Rejection")
    @allure.title("Verify Strict Rejection of Unapproved MAC Algorithms (Poly1305, SipHash)")
    @allure.description("""
        Validates that non-FIPS approved MAC algorithms (Poly1305, SipHash)
        are blocked by the FIPS provider's boundary.
    """)
    @pytest.mark.parametrize("unapproved_mac,key_hex", [
        ("POLY1305", "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"),
        ("SIPHASH", "000102030405060708090a0b0c0d0e0f")
    ])
    def test_unapproved_mac_algorithms_rejection(self, run_docker, image_tag, unapproved_mac, key_hex):
        with allure.step(f"Attempting {unapproved_mac} under strict FIPS mode"):
            result = run_docker(image_tag, [
                "mac", "-propquery", "fips=yes",
                "-macopt", f"hexkey:{key_hex}",
                unapproved_mac
            ], input_data=b"SAMPLE-PAYLOAD\n")
        assert result.returncode != 0, f"Security Breach: Unapproved MAC {unapproved_mac} was allowed under fips=yes!"
        assert any(x in result.stderr.lower() for x in ["unsupported", "invalid", "error", "failed"]), \
            f"Unexpected error: {result.stderr}"

    @allure.story("NIST SP 800-135 Application-Specific KDF")
    @allure.title("Verify ANS X9.63 Key Derivation Function (X963KDF)")
    @allure.description("""
        Validates X963KDF (SEC 1 / NIST SP 800-135) with approved SHA-256 digest.
    """)
    def test_ans_x963_kdf_functional(self, run_docker, image_tag):
        with allure.step("Deriving key using X963KDF with SHA-256"):
            result = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-keylen", "32",
                "X963KDF"
            ])
            allure.attach(result.stdout, name="X963KDF Output")
        assert result.returncode == 0, f"X963KDF failed: {result.stderr}"
        assert len(result.stdout.strip()) > 0

    @allure.story("NIST SP 800-132 Password-Based KDF Boundary")
    @allure.title("Verify NIST SP 800-132 Lower Bound Enforcement on PBKDF2 (Salt & Iterations)")
    @allure.description("""
        Validates strict enforcement of NIST SP 800-132 parameter minimums:
        - Salt length must be at least 128 bits (16 bytes); shorter salts must be rejected.
        - Iteration count must be at least 1000; smaller iteration counts must be rejected.
    """)
    def test_pbkdf2_nist_sp800_132_lower_bounds(self, run_docker, image_tag):
        with allure.step("Attempting PBKDF2 with short 8-byte salt (must fail)"):
            res_short_salt = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "pass:password",
                "-kdfopt", "hexsalt:0102030405060708",
                "-kdfopt", "iter:1000",
                "-keylen", "32",
                "PBKDF2"
            ])
            assert res_short_salt.returncode != 0, "Security Breach: PBKDF2 accepted short 8-byte salt!"
            assert "invalid salt length" in res_short_salt.stderr.lower() or "error" in res_short_salt.stderr.lower()

        with allure.step("Attempting PBKDF2 with low iteration count (iter:500, must fail)"):
            res_low_iter = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "pass:password",
                "-kdfopt", "hexsalt:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "iter:500",
                "-keylen", "32",
                "PBKDF2"
            ])
            assert res_low_iter.returncode != 0, "Security Breach: PBKDF2 accepted iteration count < 1000!"
            assert "invalid iteration count" in res_low_iter.stderr.lower() or "error" in res_low_iter.stderr.lower()

    @allure.story("NIST SP 800-135 TLS PRF")
    @allure.title("Verify TLS1-PRF Integrity (SHA-256 Approved, MD5 Rejected)")
    @allure.description("""
        Validates TLS1-PRF using approved SHA-256 digest and verifies rejection of insecure MD5.
    """)
    def test_tls1_prf_kdf(self, run_docker, image_tag):
        with allure.step("Testing TLS1-PRF with approved SHA-256"):
            res_sha256 = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "secret:tls_secret_bytes",
                "-kdfopt", "seed:client_server_random",
                "-keylen", "32",
                "TLS1-PRF"
            ])
            assert res_sha256.returncode == 0, f"TLS1-PRF SHA-256 failed: {res_sha256.stderr}"
            assert len(res_sha256.stdout.strip()) > 0

        with allure.step("Testing TLS1-PRF with unapproved MD5 (must fail)"):
            res_md5 = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:MD5",
                "-kdfopt", "secret:tls_secret_bytes",
                "-kdfopt", "seed:client_server_random",
                "-keylen", "32",
                "TLS1-PRF"
            ])
            assert res_md5.returncode != 0, "Security Breach: TLS1-PRF accepted insecure MD5!"

    @allure.story("Unapproved KDF Rejection")
    @allure.title("Verify Strict Rejection of Unapproved KDFs (SCRYPT, KRB5KDF)")
    @allure.description("""
        Validates that non-FIPS approved KDF algorithms (SCRYPT, KRB5KDF)
        are blocked by the FIPS provider's boundary.
    """)
    @pytest.mark.parametrize("unapproved_kdf,extra_opts", [
        ("SCRYPT", ["-kdfopt", "pass:password", "-kdfopt", "hexsalt:0102030405060708090a0b0c0d0e0f10"]),
        ("KRB5KDF", ["-kdfopt", "cipher:AES-128-CBC", "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10"])
    ])
    def test_unapproved_kdf_rejection(self, run_docker, image_tag, unapproved_kdf, extra_opts):
        with allure.step(f"Attempting {unapproved_kdf} under strict FIPS mode"):
            cmd = ["kdf", "-propquery", "fips=yes"] + extra_opts + ["-keylen", "16", unapproved_kdf]
            result = run_docker(image_tag, cmd)
        assert result.returncode != 0, f"Security Breach: Unapproved KDF {unapproved_kdf} was allowed under fips=yes!"

    @allure.story("NIST SP 800-108 Key-Based KDF")
    @allure.title("Verify KBKDF Counter Mode (HMAC-SHA256 Approved, MD5 Blocked)")
    def test_kbkdf_sp800_108_counter_mode(self, run_docker, image_tag):
        with allure.step("Executing KBKDF Counter mode with approved SHA-256"):
            res_pass = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "mode:counter",
                "-kdfopt", "mac:HMAC",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "hexsalt:11223344",
                "-kdfopt", "hexinfo:55667788",
                "-keylen", "32",
                "KBKDF"
            ])
            assert res_pass.returncode == 0, f"KBKDF SHA-256 failed: {res_pass.stderr}"
            assert len(res_pass.stdout.strip()) > 0

        with allure.step("Attempting KBKDF Counter mode with unapproved MD5 (must fail)"):
            res_fail = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "mode:counter",
                "-kdfopt", "mac:HMAC",
                "-kdfopt", "digest:MD5",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "hexsalt:11223344",
                "-kdfopt", "hexinfo:55667788",
                "-keylen", "32",
                "KBKDF"
            ])
            assert res_fail.returncode != 0, "Security Breach: KBKDF accepted unapproved MD5 digest!"

    @allure.story("NIST SP 800-135 SSH KDF")
    @allure.title("Verify SSHKDF Protocol Derivation (SHA-256 Approved, MD5 Blocked)")
    def test_sshkdf_sp800_135(self, run_docker, image_tag):
        with allure.step("Executing SSHKDF with approved SHA-256"):
            res_pass = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "hexxcghash:0102030405060708",
                "-kdfopt", "hexsession_id:11223344",
                "-kdfopt", "type:A",
                "-keylen", "32",
                "SSHKDF"
            ])
            assert res_pass.returncode == 0, f"SSHKDF SHA-256 failed: {res_pass.stderr}"
            assert len(res_pass.stdout.strip()) > 0

        with allure.step("Attempting SSHKDF with unapproved MD5 (must fail)"):
            res_fail = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:MD5",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "hexxcghash:0102030405060708",
                "-kdfopt", "hexsession_id:11223344",
                "-kdfopt", "type:A",
                "-keylen", "32",
                "SSHKDF"
            ])
            assert res_fail.returncode != 0, "Security Breach: SSHKDF accepted unapproved MD5 digest!"

    @allure.story("NIST SP 800-135 TLS 1.3 KDF")
    @allure.title("Verify TLS13-KDF Key Expansion (SHA-256 Approved, MD5 Blocked)")
    def test_tls13_kdf_sp800_135(self, run_docker, image_tag):
        with allure.step("Executing TLS13-KDF with approved SHA-256"):
            res_pass = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "mode:EXPAND_ONLY",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f100102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "prefix:tls13 ",
                "-kdfopt", "label:derived",
                "-keylen", "32",
                "TLS13-KDF"
            ])
            assert res_pass.returncode == 0, f"TLS13-KDF SHA-256 failed: {res_pass.stderr}"
            assert len(res_pass.stdout.strip()) > 0

        with allure.step("Attempting TLS13-KDF with unapproved MD5 (must fail)"):
            res_fail = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "mode:EXPAND_ONLY",
                "-kdfopt", "digest:MD5",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f100102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "prefix:tls13 ",
                "-kdfopt", "label:derived",
                "-keylen", "32",
                "TLS13-KDF"
            ])
            assert res_fail.returncode != 0, "Security Breach: TLS13-KDF accepted unapproved MD5 digest!"

    @allure.story("NIST SP 800-56C One-Step KDF")
    @allure.title("Verify SSKDF Functional Integrity (SHA-256 Approved, MD5 Blocked)")
    def test_sskdf_sp800_56c(self, run_docker, image_tag):
        with allure.step("Executing SSKDF with approved SHA-256"):
            res_pass = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "hexinfo:01020304",
                "-keylen", "32",
                "SSKDF"
            ])
            assert res_pass.returncode == 0, f"SSKDF SHA-256 failed: {res_pass.stderr}"
            assert len(res_pass.stdout.strip()) > 0

        with allure.step("Attempting SSKDF with unapproved MD5 (must fail)"):
            res_fail = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:MD5",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "hexinfo:01020304",
                "-keylen", "32",
                "SSKDF"
            ])
            assert res_fail.returncode != 0, "Security Breach: SSKDF accepted unapproved MD5 digest!"

    @allure.story("ANS X9.63 Key Derivation")
    @allure.title("Verify X963KDF Functional Integrity (SHA-256 Approved, MD5 Blocked)")
    def test_x963_kdf(self, run_docker, image_tag):
        with allure.step("Executing X963KDF with approved SHA-256"):
            res_pass = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:SHA256",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "hexinfo:01020304",
                "-keylen", "32",
                "X963KDF"
            ])
            assert res_pass.returncode == 0, f"X963KDF SHA-256 failed: {res_pass.stderr}"
            assert len(res_pass.stdout.strip()) > 0

        with allure.step("Attempting X963KDF with unapproved MD5 (must fail)"):
            res_fail = run_docker(image_tag, [
                "kdf", "-propquery", "fips=yes",
                "-kdfopt", "digest:MD5",
                "-kdfopt", "hexkey:0102030405060708090a0b0c0d0e0f10",
                "-kdfopt", "hexinfo:01020304",
                "-keylen", "32",
                "X963KDF"
            ])
            assert res_fail.returncode != 0, "Security Breach: X963KDF accepted unapproved MD5 digest!"

    @allure.story("PKCS#12 KDF Enforcement")
    @allure.title("Verify Rejection of Legacy PKCS12KDF and Success of PBMAC1-PBKDF2")
    def test_pkcs12_kdf_strict_isolation(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/pkcs12"

            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "req", "-x509", "-newkey", "rsa:2048",
                "-keyout", f"{container_dir}/user.key", "-nodes",
                "-out", f"{container_dir}/user.crt",
                "-sha256", "-subj", "/CN=PKCS12Test"
            ], check=True)

            with allure.step("Attempting default PKCS#12 export (uses unapproved PKCS12KDF, must fail)"):
                res_legacy = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkcs12", "-export", "-propquery", "fips=yes",
                    "-in", f"{container_dir}/user.crt",
                    "-inkey", f"{container_dir}/user.key",
                    "-out", f"{container_dir}/legacy.p12",
                    "-passout", "pass:testpass"
                ], capture_output=True, text=True)
                assert res_legacy.returncode != 0, "Security Breach: PKCS#12 export allowed unapproved PKCS12KDF!"
                assert "pkcs12kdf" in res_legacy.stderr.lower() or "error" in res_legacy.stderr.lower()

            with allure.step("Exporting PKCS#12 bundle using approved -pbmac1_pbkdf2"):
                res_fips = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkcs12", "-export", "-propquery", "fips=yes",
                    "-pbmac1_pbkdf2",
                    "-in", f"{container_dir}/user.crt",
                    "-inkey", f"{container_dir}/user.key",
                    "-out", f"{container_dir}/approved.p12",
                    "-passout", "pass:testpass"
                ], capture_output=True, text=True)
                assert res_fips.returncode == 0, f"PKCS#12 pbmac1 export failed: {res_fips.stderr}"

            with allure.step("Verifying PKCS#12 bundle import and parsing under FIPS"):
                res_import = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkcs12", "-propquery", "fips=yes",
                    "-in", f"{container_dir}/approved.p12",
                    "-passin", "pass:testpass", "-nodes"
                ], capture_output=True, text=True)
                assert res_import.returncode == 0, f"PKCS#12 import failed: {res_import.stderr}"
                assert "BEGIN CERTIFICATE" in res_import.stdout