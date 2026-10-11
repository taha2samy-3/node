import pytest
import allure

@allure.feature("Cryptographic Algorithms")
class TestMessageDigests:

    @allure.story("Hash Functions & Message Digests")
    @allure.title("Verify MD5 Algorithm Rejection")
    @allure.description("""
        Validates that the MD5 message digest algorithm is strictly prohibited.
        Any attempt to invoke MD5 via the provider must result in a failure state,
        returning an error indicating that the algorithm is unsupported or fetch failed.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("hashing", "md5", "compliance", "negative-test")
    def test_md5_execution_rejection(self, run_docker, image_tag):
        with allure.step("Attempting to execute MD5 digest calculation"):
            result = run_docker(image_tag, ["dgst", "-md5", "/dev/null"])
            allure.attach(result.stderr, name="Error Output", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying rejection logic"):
            assert result.returncode != 0, "Security Breach: MD5 algorithm execution succeeded in FIPS mode."
            
            error_msg = result.stderr.lower()
            rejection_indicators = ["unsupported", "fetch failed", "properties", "unknown", "invalid"]
            
            assert any(indicator in error_msg for indicator in rejection_indicators), \
                f"MD5 failed but with an unexpected error message: {result.stderr}"

        with allure.step("Recording compliance metric"):
            allure.dynamic.parameter("Algorithm", "MD5")
            allure.dynamic.parameter("Enforcement", "Strict Rejection")

    @allure.story("Hash Functions & Message Digests")
    @allure.title("Verify SHA-256 Algorithm Availability")
    @allure.description("""
        Confirms that the SHA-256 algorithm (SHA-2 Family) is fully operational.
        This is a blocker requirement as it is the standard hashing algorithm for FIPS 140-3.
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("hashing", "sha256", "core-functionality")
    def test_sha256_availability(self, run_docker, image_tag):
        with allure.step("Calculating SHA-256 digest for empty input"):
            result = run_docker(image_tag, ["dgst", "-sha256", "/dev/null"])
            allure.attach(result.stdout, name="Digest Output", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying digest generation integrity"):
            assert result.returncode == 0, f"SHA-256 execution failed. Stderr: {result.stderr}"
            assert "SHA256" in result.stdout or "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" in result.stdout

        with allure.step("Recording availability metric"):
            allure.dynamic.parameter("Algorithm", "SHA-256")
            allure.dynamic.parameter("Status", "Operational")

    @allure.story("Hash Functions & Message Digests")
    @allure.title("Verify SHA-3 Algorithm Availability")
    @allure.description("""
        Validates the availability of the SHA-3 family (NIST SP 800-202).
        Ensures that modern KMAC and SHAKE functions have the necessary underlying primitives.
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("hashing", "sha3", "nist-sp-800-202")
    def test_sha3_availability(self, run_docker, image_tag):
        with allure.step("Calculating SHA3-256 digest"):
            result = run_docker(image_tag, ["dgst", "-sha3-256", "/dev/null"])
            allure.attach(result.stdout, name="SHA-3 Output", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying SHA-3 functionality"):
            assert result.returncode == 0, f"SHA-3 execution failed. Stderr: {result.stderr}"
            assert "SHA3-256" in result.stdout

        with allure.step("Recording SHA-3 support"):
            allure.dynamic.parameter("Algorithm", "SHA3-256")
            allure.dynamic.parameter("Standard", "FIPS 202")


    @allure.story("Hash Functions & Message Digests")
    @allure.title("Verify SHAKE XOF Functionality")
    @allure.description("""
        Validates the functionality of SHAKE128 (Extendable Output Function).
        Ensures the algorithm is available and functional within the FIPS boundary.
        Accepts both 'SHAKE128' and 'SHAKE-128' naming conventions.
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("hashing", "shake128", "xof", "fips-202")
    def test_shake_xof_functionality(self, run_docker, image_tag):
        with allure.step("Attempting SHAKE128 digest calculation"):
            result = run_docker(image_tag, [
                "dgst", 
                "-propquery", "fips=yes", 
                "-shake128", 
                "/dev/null"
            ])
            
            allure.attach(result.stdout, name="Stdout", attachment_type=allure.attachment_type.TEXT)
            allure.attach(result.stderr, name="Stderr", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying algorithm execution and output format"):
            assert result.returncode == 0, f"SHAKE128 execution failed. Stderr: {result.stderr}"
            
            output_clean = result.stdout.upper().replace("-", "")
            assert "SHAKE128" in output_clean, f"Unexpected output format for SHAKE128. Output: {result.stdout}"

        with allure.step("Recording XOF compliance metrics"):
            allure.dynamic.parameter("Algorithm", "SHAKE128/SHAKE-128")
            allure.dynamic.parameter("Status", "Operational")

    @allure.story("Hash Functions & Message Digests")
    @allure.title("Verify Complete FIPS 180-4 SHA-2 Family Availability")
    @allure.description("""
        Validates that all standard members of the SHA-2 family (SHA-224, SHA-384, SHA-512)
        are available and functional under FIPS 140-3 approved mode.
    """)
    @pytest.mark.parametrize("digest_name", ["sha224", "sha384", "sha512"])
    def test_sha2_family_exhaustive(self, run_docker, image_tag, digest_name):
        with allure.step(f"Calculating {digest_name.upper()} digest"):
            result = run_docker(image_tag, ["dgst", "-propquery", "fips=yes", f"-{digest_name}", "/dev/null"])
            allure.attach(result.stdout, name=f"{digest_name} Output", attachment_type=allure.attachment_type.TEXT)

        with allure.step(f"Verifying {digest_name.upper()} execution integrity"):
            assert result.returncode == 0, f"{digest_name.upper()} execution failed. Stderr: {result.stderr}"
            assert len(result.stdout.strip()) > 0

    @allure.story("Hash Functions & Message Digests")
    @allure.title("Verify Complete FIPS 202 SHA-3 & SHAKE Family Availability")
    @allure.description("""
        Validates that all standard members of the SHA-3 family (SHA3-224, SHA3-384, SHA3-512)
        and SHAKE-256 XOF are operational within the FIPS cryptographic boundary.
    """)
    @pytest.mark.parametrize("digest_name", ["sha3-224", "sha3-384", "sha3-512", "shake256"])
    def test_sha3_family_exhaustive(self, run_docker, image_tag, digest_name):
        with allure.step(f"Calculating {digest_name.upper()} digest"):
            result = run_docker(image_tag, ["dgst", "-propquery", "fips=yes", f"-{digest_name}", "/dev/null"])
            allure.attach(result.stdout, name=f"{digest_name} Output", attachment_type=allure.attachment_type.TEXT)

        with allure.step(f"Verifying {digest_name.upper()} execution integrity"):
            assert result.returncode == 0, f"{digest_name.upper()} execution failed. Stderr: {result.stderr}"
            assert len(result.stdout.strip()) > 0

    @allure.story("Hash Functions & Message Digests")
    @allure.title("Verify Strict Rejection of Non-Approved Digests (MD2, MD4, RIPEMD-160, MDC2)")
    @allure.description("""
        Validates the strict negative boundary: obsolete and unapproved message digests
        (MD2, MD4, RIPEMD-160, MDC2) must be strictly unavailable and rejected in FIPS mode.
    """)
    @pytest.mark.parametrize("unapproved_digest", ["md2", "md4", "rmd160", "mdc2"])
    def test_unapproved_digests_rejection(self, run_docker, image_tag, unapproved_digest):
        with allure.step(f"Attempting to invoke unapproved digest {unapproved_digest}"):
            result = run_docker(image_tag, ["dgst", "-propquery", "fips=yes", f"-{unapproved_digest}", "/dev/null"])
            allure.attach(result.stderr, name=f"{unapproved_digest} Error", attachment_type=allure.attachment_type.TEXT)

        with allure.step(f"Verifying strict rejection of {unapproved_digest}"):
            assert result.returncode != 0, f"Security Breach: Non-approved digest {unapproved_digest} succeeded in FIPS mode!"
            error_msg = result.stderr.lower()
            assert any(x in error_msg for x in ["unsupported", "unknown", "fetch failed", "invalid", "error"]), \
                f"Unexpected error for {unapproved_digest}: {result.stderr}"

    @allure.story("Hash Functions & Message Digests")
    @allure.title("Verify Truncated SHA-512 Variants (SHA-512/224, SHA-512/256)")
    @allure.description("""
        Validates NIST FIPS 180-4 approved truncated variants of SHA-512:
        SHA-512/224 and SHA-512/256.
    """)
    @pytest.mark.parametrize("variant", ["sha512-224", "sha512-256"])
    def test_sha2_truncated_variants(self, run_docker, image_tag, variant):
        with allure.step(f"Testing {variant}"):
            result = run_docker(image_tag, ["dgst", "-propquery", "fips=yes", f"-{variant}", "/dev/null"])
            assert result.returncode == 0, f"{variant} failed: {result.stderr}"
            assert len(result.stdout.strip()) > 0

    @allure.story("Known Answer Tests (KAT)")
    @allure.title("Verify NIST FIPS 180-4 and FIPS 202 Known Answer Tests")
    @allure.description("""
        Validates cryptographic precision against official NIST Known Answer Test (KAT) vectors.
    """)
    @pytest.mark.parametrize("digest,expected_hash", [
        ("sha224", "d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f"),
        ("sha256", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        ("sha384", "38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1da274edebfe76f65fbd51ad2f14898b95b"),
        ("sha512", "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"),
        ("sha3-224", "6b4e03423667dbb73b6e15454f0eb1abd4597f9a1b078e3f5b5a6bc7"),
        ("sha3-256", "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"),
        ("sha3-384", "0c63a75b845e4f7d01107d852e4c2485c51a50aaaa94fc61995e71bbee983a2ac3713831264adb47fb6bd1e058d5f004"),
        ("sha3-512", "a69f73cca23a9ac5c8b567dc185a756e97c982164fe25859e0d1dcc1475c80a615b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281dcd26"),
    ])
    def test_nist_hash_known_answer_tests(self, run_docker, image_tag, digest, expected_hash):
        result = run_docker(image_tag, ["dgst", "-propquery", "fips=yes", f"-{digest}", "/dev/null"])
        assert result.returncode == 0, f"KAT execution failed for {digest}: {result.stderr}"
        actual = result.stdout.strip().split()[-1].lower()
        assert actual == expected_hash, f"KAT verification mismatch for {digest}! Got {actual}, expected {expected_hash}"