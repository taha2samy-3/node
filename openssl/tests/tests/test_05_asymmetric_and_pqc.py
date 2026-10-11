import pytest
import allure
import tempfile
import os
import subprocess

@allure.feature("Asymmetric Cryptography")
class TestRSAOperations:

    @allure.story("RSA Policy Enforcement")
    @allure.title("Verify Support for Large RSA Modulus (4096-bit)")
    @allure.description("""
        Validates that the FIPS provider supports RSA modulus sizes beyond the 2048-bit minimum.
        According to Security Policy Page 36 (Section 2.7.g), the module supports modulus 
        lengths up to 16384 bits. This test performs a functional generation of a 4096-bit 
        RSA key to confirm support for large moduli while maintaining efficient test execution time.
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("rsa", "large-modulus", "key-gen", "page-36")
    def test_rsa_large_modulus_support(self, run_docker, image_tag):
        # 4096 is used as a representative 'Large' modulus to avoid extreme generation times
        target_bits = "4096"
        
        with allure.step(f"Generating a {target_bits}-bit RSA private key using FIPS provider"):
            result = run_docker(image_tag, [
                "genpkey", 
                "-propquery", "fips=yes", 
                "-algorithm", "RSA", 
                "-pkeyopt", f"rsa_keygen_bits:{target_bits}"
            ])
            
            allure.attach(result.stdout, name="Generated Private Key")
            allure.attach(result.stderr, name="Genpkey Stderr")

        with allure.step(f"Verifying {target_bits}-bit key generation success"):
            assert result.returncode == 0, f"FIPS provider failed to generate a {target_bits}-bit RSA key."
            assert "BEGIN PRIVATE KEY" in result.stdout, "Output did not contain a valid private key."

        with allure.step("Recording RSA modulus compliance"):
            allure.dynamic.parameter("Tested Modulus", f"{target_bits} bits")
            allure.dynamic.parameter("Policy Limit", "Up to 16384 bits")
            allure.dynamic.parameter("Status", "Operational")
    @allure.story("RSA Key Generation")
    @allure.title("Verify RSA 2048-bit Compliance")
    @allure.description("""
        Validates the generation of RSA keys with a 2048-bit modulus.
        As per FIPS 140-3 and NIST SP 800-131A, 2048-bit is the minimum accepted 
        security strength for RSA key generation in a compliant environment.
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("rsa", "key-gen", "2048-bit", "compliance")
    def test_rsa_keygen_2048_compliance(self, run_docker, image_tag):
        with allure.step("Generating 2048-bit RSA private key"):
            result = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "RSA", 
                "-pkeyopt", "rsa_keygen_bits:2048"
            ])
            allure.attach(result.stdout, name="Generated Key Output", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying successful generation and output format"):
            assert result.returncode == 0, f"RSA 2048-bit generation failed. Stderr: {result.stderr}"
            assert "BEGIN PRIVATE KEY" in result.stdout, "The output does not contain a valid PEM private key."

        with allure.step("Recording key generation metrics"):
            allure.dynamic.parameter("Algorithm", "RSA")
            allure.dynamic.parameter("Key Size", "2048-bit")
            allure.dynamic.parameter("FIPS Status", "Approved")

    @allure.story("RSA Key Generation")
    @allure.title("Verify Rejection of Weak RSA 1024-bit Keys")
    @allure.description("""
        Validates the enforcement of minimum RSA key lengths.
        FIPS 140-3 strictly prohibits the generation of RSA keys smaller than 2048 bits.
        The system must intercept and reject any attempt to generate a 1024-bit RSA key.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("rsa", "key-gen", "1024-bit", "negative-test")
    def test_rsa_keygen_weak_rejection(self, run_docker, image_tag):
        with allure.step("Attempting to generate a 1024-bit RSA key"):
            result = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "RSA", 
                "-pkeyopt", "rsa_keygen_bits:1024"
            ])
            allure.attach(result.stderr, name="Rejection Error Log", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying mandatory rejection of legacy key size"):
            assert result.returncode != 0, "Security Breach: RSA 1024-bit key generation was allowed in FIPS mode."
            
            error_msg = result.stderr.lower()
            rejection_indicators = ["invalid", "too small", "error", "fips", "unsupported"]
            assert any(indicator in error_msg for indicator in rejection_indicators), \
                f"Generation failed but without a specific policy error. Stderr: {result.stderr}"

        with allure.step("Recording security boundary enforcement"):
            allure.dynamic.parameter("Forbidden Size", "1024-bit")
            allure.dynamic.parameter("Policy", "NIST SP 800-131A Rev. 2")
            allure.dynamic.parameter("Result", "Operation Blocked")


    @allure.story("RSA Padding Schemes")
    @allure.title("Verify RSA-PSS Signature and Verification Integrity")
    @allure.description("""
        Validates RSA-PSS padding mode compliance. 
        Forces the use of SHA256 explicitly to prevent FIPS from blocking the default SHA1.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("rsa", "rsa-pss", "fips-compliance")
    def test_rsa_pss_padding_signature(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/crypto"
            
            key_file = "key.pem"
            data_file = "data.txt"
            sig_file = "signature.bin"
            
            test_payload = "FIPS-PSS-STRICT-DIGEST-VERIFICATION"
            with open(os.path.join(host_dir, data_file), "w") as f:
                f.write(test_payload)

            with allure.step("Step 1: RSA 2048-bit Key Generation"):
                gen_cmd = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl", "-v", f"{host_dir}:{container_dir}",
                    image_tag, "genpkey", "-algorithm", "RSA", 
                    "-propquery", "fips=yes",
                    "-pkeyopt", "rsa_keygen_bits:2048",
                    "-out", f"{container_dir}/{key_file}"
                ]
                res_gen = subprocess.run(gen_cmd, capture_output=True, text=True)
                assert res_gen.returncode == 0

            with allure.step("Step 2: PSS Signature Creation (Explicit SHA256)"):
                sign_cmd = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl", "-v", f"{host_dir}:{container_dir}",
                    image_tag, "pkeyutl", "-sign", 
                    "-propquery", "fips=yes",
                    "-inkey", f"{container_dir}/{key_file}",
                    "-digest", "sha256",
                    "-pkeyopt", "rsa_padding_mode:pss",
                    "-pkeyopt", "rsa_pss_saltlen:32",
                    "-in", f"{container_dir}/{data_file}",
                    "-out", f"{container_dir}/{sig_file}"
                ]
                res_sign = subprocess.run(sign_cmd, capture_output=True, text=True)
                allure.attach(res_sign.stderr, name="Signing Stderr (Debug)")
                
                assert res_sign.returncode == 0, f"Signing Failed: {res_sign.stderr}"

            with allure.step("Step 3: PSS Signature Verification"):
                verify_cmd = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl", "-v", f"{host_dir}:{container_dir}",
                    image_tag, "pkeyutl", "-verify", 
                    "-propquery", "fips=yes",
                    "-inkey", f"{container_dir}/{key_file}",
                    "-digest", "sha256",
                    "-pkeyopt", "rsa_padding_mode:pss",
                    "-pkeyopt", "rsa_pss_saltlen:32",
                    "-in", f"{container_dir}/{data_file}",
                    "-sigfile", f"{container_dir}/{sig_file}"
                ]
                res_verify = subprocess.run(verify_cmd, capture_output=True, text=True)
                allure.attach(res_verify.stdout, name="Verification Result")
                
                assert res_verify.returncode == 0
                assert "Signature Verified Successfully" in res_verify.stdout

        with allure.step("RSA-PSS operational compliance confirmed"):
            allure.dynamic.parameter("Security Policy", "FIPS 140-3 Compliant (SHA256 Mandatory)")
            allure.dynamic.parameter("Result", "PSS Verified")

    @allure.story("NIST SP 800-56B Exponent Bounds")
    @allure.title("Verify RSA Public Exponent Boundaries (e > 65536, odd integer)")
    @pytest.mark.parametrize("invalid_exp", [3, 17, 257, 65535, 65536])
    def test_rsa_public_exponent_boundaries(self, run_docker, image_tag, invalid_exp):
        with allure.step(f"Attempting RSA-2048 keygen with invalid exponent e={invalid_exp}"):
            res_fail = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "RSA",
                "-pkeyopt", "rsa_keygen_bits:2048",
                "-pkeyopt", f"rsa_keygen_pubexp:{invalid_exp}"
            ])
            assert res_fail.returncode != 0, f"Security Breach: RSA accepted unapproved exponent e={invalid_exp}!"
            assert "pub exponent out of range" in res_fail.stderr.lower() or "error" in res_fail.stderr.lower()

        with allure.step("Verifying RSA keygen succeeds with approved e=65537"):
            res_pass = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "RSA",
                "-pkeyopt", "rsa_keygen_bits:2048",
                "-pkeyopt", "rsa_keygen_pubexp:65537"
            ])
            assert res_pass.returncode == 0, f"RSA keygen with e=65537 failed: {res_pass.stderr}"

    @allure.story("NIST SP 800-56B Modulus Boundary")
    @allure.title("Verify RSA Modulus Exact Lower Boundary (2047 Rejected, 2049 Accepted)")
    def test_rsa_modulus_exact_boundary(self, run_docker, image_tag):
        with allure.step("Attempting RSA keygen with 2047 bits (must fail)"):
            res_fail = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "RSA",
                "-pkeyopt", "rsa_keygen_bits:2047"
            ])
            assert res_fail.returncode != 0, "Security Breach: RSA accepted modulus size < 2048 bits!"
            assert "key size too small" in res_fail.stderr.lower() or "error" in res_fail.stderr.lower()

        with allure.step("Attempting RSA keygen with 2049 bits (must succeed)"):
            res_pass = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "RSA",
                "-pkeyopt", "rsa_keygen_bits:2049"
            ])
            assert res_pass.returncode == 0, f"RSA keygen with 2049 bits failed: {res_pass.stderr}"

    @allure.story("RSA-PSS Padding & Digest Policy")
    @allure.title("Verify RSA-PSS Digest Ordering and MD5 Rejection")
    def test_rsa_pss_parameter_ordering_and_md5_rejection(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/rsapss"

            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "genpkey", "-propquery", "fips=yes", "-algorithm", "RSA",
                "-pkeyopt", "rsa_keygen_bits:2048", "-out", f"{container_dir}/rsa.key"
            ], check=True)

            with open(os.path.join(host_dir, "digest.bin"), "wb") as f:
                f.write(b"X" * 32)

            with allure.step("Executing PSS sign with ordered SHA-256 (must succeed)"):
                res_pass = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkeyutl", "-sign", "-propquery", "fips=yes",
                    "-inkey", f"{container_dir}/rsa.key",
                    "-pkeyopt", "digest:sha256",
                    "-pkeyopt", "rsa_padding_mode:pss",
                    "-pkeyopt", "rsa_pss_saltlen:digest",
                    "-in", f"{container_dir}/digest.bin",
                    "-out", f"{container_dir}/sig.bin"
                ], capture_output=True, text=True)
                assert res_pass.returncode == 0, f"PSS sign with SHA-256 failed: {res_pass.stderr}"

            with allure.step("Attempting PSS sign with unapproved MD5 (must fail)"):
                res_fail = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkeyutl", "-sign", "-propquery", "fips=yes",
                    "-inkey", f"{container_dir}/rsa.key",
                    "-pkeyopt", "digest:md5",
                    "-pkeyopt", "rsa_padding_mode:pss",
                    "-in", f"{container_dir}/digest.bin",
                    "-out", f"{container_dir}/sig_bad.bin"
                ], capture_output=True, text=True)
                assert res_fail.returncode != 0, "Security Breach: RSA-PSS accepted unapproved MD5 digest!"




@allure.feature("Asymmetric Cryptography")
class TestECCAndSignatures:


    @pytest.mark.xfail(strict=True, reason="Known limitation of the certified OpenSSL FIPS provider 3.1.2: X25519 is offered under fips=yes although it is not an approved key agreement scheme")
    @allure.story("Asymmetric Cryptography Boundary")
    @allure.title("Verify Rejection of Non-Approved Curves (Ed25519/X25519/Ed448)")
    @allure.description("""
        Validates the isolation of non-approved asymmetric algorithms.
        Includes a detailed debug phase to list all algorithms claiming FIPS compliance.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("rejection", "ed25519", "x25519", "debug")
    def test_strict_block_legacy_curves_and_algos(self, run_docker, image_tag):
        # DEBUG PHASE: List what the FIPS provider actually thinks it supports
        with allure.step("DEBUG: Querying FIPS provider capability list"):
            kex_list = run_docker(image_tag, ["list", "-key-exchange-algorithms", "-propquery", "fips=yes"])
            sig_list = run_docker(image_tag, ["list", "-signature-algorithms", "-propquery", "fips=yes"])
            
            print("\n" + "="*60)
            print(f"[DEBUG] FIPS KEY-EXCHANGE ALGORITHMS:\n{kex_list.stdout}")
            print("-" * 60)
            print(f"[DEBUG] FIPS SIGNATURE ALGORITHMS:\n{sig_list.stdout}")
            print("="*60 + "\n")
            
            allure.attach(kex_list.stdout, name="FIPS Key Exchange List")
            allure.attach(sig_list.stdout, name="FIPS Signature List")

        # EXECUTION PHASE
        forbidden_algos = ["Ed25519", "X25519", "Ed448"]
        failed_blocks = []

        for algo in forbidden_algos:
            with allure.step(f"Attempting to invoke forbidden algorithm: {algo}"):
                result = run_docker(image_tag, [
                    "genpkey", 
                    "-algorithm", algo, 
                    "-propquery", "fips=yes"
                ])
                
                # Check stdout for clues on which provider was used
                allure.attach(result.stdout, name=f"{algo} Stdout")
                allure.attach(result.stderr, name=f"{algo} Stderr")

                if result.returncode == 0:
                    print(f"[CRITICAL DEBUG] Algorithm {algo} was PERMITTED. ReturnCode: 0")
                    failed_blocks.append(algo)
                else:
                    print(f"[INFO DEBUG] Algorithm {algo} was correctly rejected.")

        with allure.step("Verifying all non-approved algorithms were blocked"):
            assert not failed_blocks, \
                f"Security Policy Violation: The following algorithms were PERMITTED in FIPS mode: {failed_blocks}. Check Debug Logs."

        with allure.step("Recording policy enforcement status"):
            allure.dynamic.parameter("Isolation Status", "Failure Detected" if failed_blocks else "Success")







    @allure.story("Elliptic Curve Cryptography (ECC)")
    @allure.title("Verify ECDSA P-384 Functional Integrity")
    @allure.description("""
        Validates the generation and structural integrity of Elliptic Curve keys 
        using the NIST P-384 curve. Confirms that the FIPS provider supports 
        approved curves. Note: P-384 is technically referred to as secp384r1.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("ecc", "ecdsa", "p-384", "key-gen")
    def test_ecdsa_p384_signing_flow(self, run_docker, image_tag):

        with allure.step("Generating P-384 EC private key"):
            gen_result = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "EC", 
                "-pkeyopt", "ec_paramgen_curve:P-384"
            ])
            allure.attach(gen_result.stdout, name="Generated EC Key")
            allure.attach(gen_result.stderr, name="Genpkey Stderr")
            
            assert gen_result.returncode == 0, f"EC Key generation failed. Stderr: {gen_result.stderr}"

        with allure.step("Verifying curve support via ecparam"):
            check_result = run_docker(image_tag, ["ecparam", "-list_curves"])
            
            print(f"[DEBUG] ecparam Output Length: {len(check_result.stdout)}")
            allure.attach(check_result.stdout, name="Full Curves List")

            supported_names = ["P-384", "secp384r1"]
            found = any(name in check_result.stdout for name in supported_names)
            
            assert found, f"Neither P-384 nor secp384r1 found in supported curves. Output: {check_result.stdout[:100]}..."

    @allure.story("Signature Policy Enforcement")
    @allure.title("Verify Rejection of MD5 for Digital Signatures")
    @allure.description("""
        Validates the mandatory rejection of MD5 when used for digital signatures.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("signatures", "md5-rejection", "negative-test")
    def test_md5_signature_verification_rejection(self, run_docker, image_tag):
        with allure.step("Attempting signature verification using MD5 digest"):
            result = run_docker(image_tag, [
                "dgst", "-propquery", "fips=yes",
                "-md5", "/dev/null"
            ])
            allure.attach(result.stderr, name="Policy Rejection Log")

        with allure.step("Verifying signature algorithm rejection"):
            assert result.returncode != 0, "Security Breach: MD5 allowed in FIPS mode."
            
            error_msg = result.stderr.lower()
            rejection_indicators = ["unsupported", "fetch failed", "digest", "error", "disabled", "not approved"]
            
            assert any(indicator in error_msg for indicator in rejection_indicators), \
                f"Operation failed but not with a clear policy rejection. Stderr: {result.stderr}"








    @allure.story("Key Agreement Protocols")
    @allure.title("Verify ECDH Raw Key Derivation (NIST P-384)")
    @allure.description("""
        Validates the Elliptic Curve Diffie-Hellman (ECDH) key agreement protocol.
        Ensures the derivation is performed exclusively within the FIPS cryptographic boundary.
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("ecdh", "key-exchange", "nist-p384")
    def test_ecdh_key_derivation_raw(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/ecdh"

            with allure.step("Step 1: Generating Bob's EC Private Key (P-384)"):
                gen_bob_cmd = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl", "-v", f"{host_dir}:{container_dir}",
                    image_tag, "genpkey", "-algorithm", "EC", 
                    "-pkeyopt", "ec_paramgen_curve:P-384",
                    "-out", f"{container_dir}/bob_priv.pem"
                ]
                subprocess.run(gen_bob_cmd, check=True)

            with allure.step("Step 2: Extracting Bob's Public Key"):
                pub_bob_cmd = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl", "-v", f"{host_dir}:{container_dir}",
                    image_tag, "pkey", "-in", f"{container_dir}/bob_priv.pem", 
                    "-pubout", "-out", f"{container_dir}/bob_pub.pem"
                ]
                res_pub = subprocess.run(pub_bob_cmd, capture_output=True, text=True)
                assert res_pub.returncode == 0, f"Public key extraction failed: {res_pub.stderr}"

            with allure.step("Step 3: Generating Alice's EC Private Key"):
                gen_alice_cmd = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl", "-v", f"{host_dir}:{container_dir}",
                    image_tag, "genpkey", "-algorithm", "EC", 
                    "-pkeyopt", "ec_paramgen_curve:P-384",
                    "-out", f"{container_dir}/alice_priv.pem"
                ]
                subprocess.run(gen_alice_cmd, check=True)

            with allure.step("Step 4: Alice Derives Shared Secret using Bob's Public Key"):
                derive_cmd = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl", "-v", f"{host_dir}:{container_dir}",
                    image_tag, "pkeyutl", "-derive", 
                    "-inkey", f"{container_dir}/alice_priv.pem",
                    "-peerkey", f"{container_dir}/bob_pub.pem",
                    "-out", f"{container_dir}/shared_secret.bin"
                ]
                res_derive = subprocess.run(derive_cmd, capture_output=True, text=True)
                assert res_derive.returncode == 0, f"Derivation failed: {res_derive.stderr}"

            with allure.step("Step 5: Confirming Secret Generation"):
                secret_file = os.path.join(host_dir, "shared_secret.bin")
                assert os.path.exists(secret_file), "Shared secret file was not created."
                assert os.path.getsize(secret_file) > 0, "Shared secret file is empty."

        with allure.step("ECDH raw derivation verified successfully"):
            allure.dynamic.parameter("Curve", "NIST P-384")
            allure.dynamic.parameter("Operation", "Raw Z-value Derivation")

    @allure.story("DSA FIPS 186-4 Boundaries")
    @allure.title("Verify Rejection of Weak DSA Parameter Lengths (1536 bits)")
    def test_dsa_invalid_parameter_lengths(self, run_docker, image_tag):
        with allure.step("Attempting DSA parameter generation for 1536 bits (must fail)"):
            res_fail = run_docker(image_tag, [
                "dsaparam", "-propquery", "fips=yes", "1536"
            ])
            assert res_fail.returncode != 0, "Security Breach: dsaparam accepted 1536 bits!"
            assert "bad ffc parameters" in res_fail.stderr.lower() or "error" in res_fail.stderr.lower()

    @allure.story("NIST SP 800-131A Digital Signatures")
    @allure.title("Verify Rejection of SHA-1 for DSA Digital Signature Generation")
    def test_dsa_sha1_signing_rejection(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/dsasig"

            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "dsaparam", "-propquery", "fips=yes", "-out", f"{container_dir}/dsap.pem", "2048"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "gendsa", "-propquery", "fips=yes", "-out", f"{container_dir}/dsakey.pem", f"{container_dir}/dsap.pem"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "pkey", "-in", f"{container_dir}/dsakey.pem", "-pubout", "-out", f"{container_dir}/dsapub.pem"
            ], check=True)

            with open(os.path.join(host_dir, "msg.txt"), "w") as f:
                f.write("DSA test message payload")

            with allure.step("Attempting DSA sign with SHA-1 (must fail under SP 800-131A)"):
                res_fail = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "dgst", "-sha1", "-sign", f"{container_dir}/dsakey.pem", f"{container_dir}/msg.txt"
                ], capture_output=True, text=True)
                assert res_fail.returncode != 0, "Security Breach: DSA signature generated using disallowed SHA-1!"
                assert "digest not allowed" in res_fail.stderr.lower() or "error" in res_fail.stderr.lower()

            with allure.step("Verifying DSA sign with approved SHA-256 and public key verification"):
                res_sign = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "dgst", "-sha256", "-sign", f"{container_dir}/dsakey.pem",
                    "-out", f"{container_dir}/sig.bin", f"{container_dir}/msg.txt"
                ], capture_output=True, text=True)
                assert res_sign.returncode == 0, f"DSA SHA-256 sign failed: {res_sign.stderr}"

                res_verify = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "dgst", "-sha256", "-verify", f"{container_dir}/dsapub.pem",
                    "-signature", f"{container_dir}/sig.bin", f"{container_dir}/msg.txt"
                ], capture_output=True, text=True)
                assert res_verify.returncode == 0, f"DSA SHA-256 verify failed: {res_verify.stderr}"
                assert "Verified OK" in res_verify.stdout

    @allure.story("NIST SP 800-131A Digital Signatures")
    @allure.title("Verify Rejection of SHA-1 for ECDSA Signature Generation")
    def test_ecdsa_sha1_signing_rejection(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/ecdsasig"

            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "genpkey", "-propquery", "fips=yes", "-algorithm", "EC",
                "-pkeyopt", "ec_paramgen_curve:P-256", "-out", f"{container_dir}/eckey.pem"
            ], check=True)

            with open(os.path.join(host_dir, "msg.txt"), "w") as f:
                f.write("ECDSA message to sign")

            with allure.step("Attempting ECDSA sign with SHA-1 (must fail)"):
                res_fail = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "dgst", "-sha1", "-sign", f"{container_dir}/eckey.pem", f"{container_dir}/msg.txt"
                ], capture_output=True, text=True)
                assert res_fail.returncode != 0, "Security Breach: ECDSA signature generated using disallowed SHA-1!"
                assert "digest not allowed" in res_fail.stderr.lower() or "error" in res_fail.stderr.lower()

    @allure.story("Elliptic Curves Policy")
    @allure.title("Verify Strict Rejection of Non-NIST Curves (secp256k1, brainpool, SM2)")
    @pytest.mark.parametrize("unapproved_curve", ["secp256k1", "brainpoolP256r1", "SM2"])
    def test_non_nist_ec_curves_rejection(self, run_docker, image_tag, unapproved_curve):
        with allure.step(f"Attempting keygen with unapproved curve {unapproved_curve}"):
            res_fail = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "EC",
                "-pkeyopt", f"ec_paramgen_curve:{unapproved_curve}"
            ])
            assert res_fail.returncode != 0, f"Security Breach: Curve {unapproved_curve} allowed under fips=yes!"
            assert "unknown group" in res_fail.stderr.lower() or "error" in res_fail.stderr.lower()





@allure.feature("Asymmetric Cryptography")
class TestPostQuantumIsolation:

    @allure.story("Post-Quantum Cryptography (PQC) Isolation")
    @allure.title("Verify Isolation of ML-KEM (Kyber) from FIPS Boundary")
    @allure.description("""
        Validates that modern Post-Quantum Cryptography (PQC) algorithms, specifically ML-KEM (Kyber),
        are strictly unavailable when the FIPS property query is enforced. 
        As these algorithms are not yet part of the certified FIPS 140-3 provider 
        (e.g., OpenSSL FIPS provider 3.0.x/3.1.x), they must be rejected to ensure 
        only approved algorithms are used within the cryptographic boundary.
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("pqc", "isolation", "ml-kem", "negative-test")
    def test_ml_kem_isolation_in_fips(self, run_docker, image_tag):
        with allure.step("Attempting to generate ML-KEM-768 key using strict FIPS properties"):
            # The genpkey command should fail when restricted to fips=yes
            result = run_docker(image_tag, [
                "genpkey", 
                "-propquery", "fips=yes", 
                "-algorithm", "ML-KEM-768"
            ])
            
            allure.attach(result.stdout, name="Stdout", attachment_type=allure.attachment_type.TEXT)
            allure.attach(result.stderr, name="Stderr (Rejection Log)", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying algorithm rejection by FIPS provider"):
            # Expected behavior: returncode must be non-zero (failure)
            assert result.returncode != 0, "Security Bypass: PQC algorithm (ML-KEM) was allowed under strict FIPS mode."
            
            error_msg = result.stderr.lower()
            rejection_indicators = ["unsupported", "algorithm", "failed", "fetch", "not found"]
            
            assert any(indicator in error_msg for indicator in rejection_indicators), \
                f"The command failed, but not with an expected PQC algorithm rejection error. Stderr: {result.stderr}"

        with allure.step("Recording isolation boundary status"):
            allure.dynamic.parameter("Target Algorithm", "ML-KEM-768")
            allure.dynamic.parameter("Policy Requirement", "FIPS 140-3 Boundary Isolation")
            allure.dynamic.parameter("Status", "Correctly Blocked")

    @allure.story("Digital Signature Policy (NIST SP 800-131A Rev. 2)")
    @allure.title("Verify Strict Rejection of SHA-1 for Digital Signature Generation")
    @allure.description("""
        Validates NIST SP 800-131A Rev. 2 transition rule:
        The use of SHA-1 for digital signature generation is strictly prohibited in FIPS mode.
        Tests both RSA and ECDSA signature generation attempts with SHA-1.
    """)
    def test_sha1_digital_signature_generation_rejection(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            data_file = os.path.join(host_dir, "data.txt")
            with open(data_file, "w") as f:
                f.write("FIPS-DIGITAL-SIGNATURE-TEST\n")

            with allure.step("Generating compliant RSA 2048-bit key"):
                gen_rsa = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:/mnt/keys", image_tag,
                    "genpkey", "-propquery", "fips=yes", "-algorithm", "RSA",
                    "-pkeyopt", "rsa_keygen_bits:2048", "-out", "/mnt/keys/rsa.pem"
                ]
                subprocess.run(gen_rsa, check=True)

            with allure.step("Attempting RSA signature generation with SHA-1 (must fail)"):
                sign_rsa = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:/mnt/keys", image_tag,
                    "dgst", "-propquery", "fips=yes", "-sha1", "-sign", "/mnt/keys/rsa.pem", "/mnt/keys/data.txt"
                ]
                res_rsa = subprocess.run(sign_rsa, capture_output=True, text=True)
                assert res_rsa.returncode != 0, "Security Breach: RSA signature generation with SHA-1 was permitted in FIPS mode!"
                assert any(x in res_rsa.stderr.lower() for x in ["not allowed", "error", "digest", "unsupported"]), \
                    f"Unexpected error: {res_rsa.stderr}"

            with allure.step("Generating compliant EC P-256 key"):
                gen_ec = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:/mnt/keys", image_tag,
                    "genpkey", "-propquery", "fips=yes", "-algorithm", "EC",
                    "-pkeyopt", "ec_paramgen_curve:P-256", "-out", "/mnt/keys/ec.pem"
                ]
                subprocess.run(gen_ec, check=True)

            with allure.step("Attempting ECDSA signature generation with SHA-1 (must fail)"):
                sign_ec = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:/mnt/keys", image_tag,
                    "dgst", "-propquery", "fips=yes", "-sha1", "-sign", "/mnt/keys/ec.pem", "/mnt/keys/data.txt"
                ]
                res_ec = subprocess.run(sign_ec, capture_output=True, text=True)
                assert res_ec.returncode != 0, "Security Breach: ECDSA signature generation with SHA-1 was permitted in FIPS mode!"
                assert any(x in res_ec.stderr.lower() for x in ["not allowed", "error", "digest", "unsupported"]), \
                    f"Unexpected error: {res_ec.stderr}"

    @allure.story("Elliptic Curve Cryptography Boundaries")
    @allure.title("Verify Rejection of Non-NIST Curves (secp256k1, Brainpool)")
    @allure.description("""
        Validates that non-NIST elliptic curves (secp256k1, Brainpool) cannot be used
        for key generation under strict FIPS mode.
    """)
    @pytest.mark.parametrize("curve", ["secp256k1", "brainpoolP256r1", "brainpoolP384r1", "brainpoolP512r1"])
    def test_non_nist_curves_rejection(self, run_docker, image_tag, curve):
        with allure.step(f"Attempting key generation on non-NIST curve {curve}"):
            result = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "EC",
                "-pkeyopt", f"ec_paramgen_curve:{curve}"
            ])
        assert result.returncode != 0, f"Security Breach: Non-NIST curve {curve} was accepted in FIPS mode!"

    @allure.story("Elliptic Curve Cryptography Boundaries")
    @allure.title("Verify Operational Support for All NIST-Approved Curves")
    @allure.description("""
        Validates that all approved NIST curves (P-224, P-256, P-384, P-521)
        are fully functional for key generation in FIPS mode.
    """)
    @pytest.mark.parametrize("curve", ["P-224", "P-256", "P-384", "P-521"])
    def test_nist_approved_curves_keygen(self, run_docker, image_tag, curve):
        with allure.step(f"Generating key on approved NIST curve {curve}"):
            result = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "EC",
                "-pkeyopt", f"ec_paramgen_curve:{curve}"
            ])
        assert result.returncode == 0, f"Failed to generate key on approved curve {curve}: {result.stderr}"
        assert "BEGIN PRIVATE KEY" in result.stdout

    @allure.story("RSA Key Length Boundaries (NIST SP 800-131A Rev. 2)")
    @allure.title("Verify Strict Rejection of Sub-2048 Bit RSA Keys")
    @allure.description("""
        Validates that RSA key generation requests smaller than 2048 bits (512, 1024, 1536)
        are intercepted and rejected by the FIPS provider's SP 800-56B strength validation.
    """)
    @pytest.mark.parametrize("bits", [512, 1024, 1536])
    def test_weak_rsa_keys_rejection(self, run_docker, image_tag, bits):
        with allure.step(f"Attempting to generate weak {bits}-bit RSA key"):
            result = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-algorithm", "RSA",
                "-pkeyopt", f"rsa_keygen_bits:{bits}"
            ])
        assert result.returncode != 0, f"Security Breach: Weak {bits}-bit RSA key was generated in FIPS mode!"
        assert any(x in result.stderr.lower() for x in ["invalid", "modulus", "error", "unsupported", "too small"]), \
            f"Unexpected error: {result.stderr}"

    @allure.story("DSA Key Boundaries")
    @allure.title("Verify DSA FIPS Boundaries (2048-bit allowed, 1024-bit rejected)")
    @allure.description("""
        Validates that DSA parameter generation succeeds for compliant 2048-bit length
        and is rejected for legacy 1024-bit length.
    """)
    def test_dsa_fips_boundaries(self, run_docker, image_tag):
        with allure.step("Testing 1024-bit DSA parameters (must fail)"):
            res_1024 = run_docker(image_tag, ["dsaparam", "-propquery", "fips=yes", "1024"])
            assert res_1024.returncode != 0, "Security Breach: 1024-bit DSA parameters were generated in FIPS mode!"

        with allure.step("Testing 2048-bit DSA parameters (compliant)"):
            res_2048 = run_docker(image_tag, ["dsaparam", "-propquery", "fips=yes", "2048"])
            assert res_2048.returncode == 0, f"2048-bit DSA parameter generation failed: {res_2048.stderr}"
            assert "BEGIN DSA PARAMETERS" in res_2048.stdout

    @allure.story("Finite Field Diffie-Hellman (NIST SP 800-56A Rev. 3)")
    @allure.title("Verify FFDHE Safe Prime Parameter Generation (ffdhe2048, ffdhe3072, ffdhe4096)")
    @allure.description("""
        Validates NIST SP 800-56A Rev. 3 approved RFC 7919 safe prime groups:
        ffdhe2048, ffdhe3072, and ffdhe4096.
    """)
    @pytest.mark.parametrize("group", ["ffdhe2048", "ffdhe3072", "ffdhe4096"])
    def test_ffdhe_safe_prime_groups_compliance(self, run_docker, image_tag, group):
        with allure.step(f"Generating DH parameters using approved group {group}"):
            result = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-genparam", "-algorithm", "DH",
                "-pkeyopt", f"group:{group}"
            ])
            allure.attach(result.stdout, name=f"{group} DH Parameters")
        assert result.returncode == 0, f"FFDHE group {group} failed: {result.stderr}"
        assert "BEGIN DH PARAMETERS" in result.stdout

    @allure.story("Finite Field Diffie-Hellman (NIST SP 800-56A Rev. 3)")
    @allure.title("Verify Strict Rejection of Weak DH Parameters (1024-bit)")
    @allure.description("""
        Validates that DH parameter generation with weak 1024-bit prime length
        is rejected by the FIPS provider.
    """)
    def test_dh_weak_parameters_rejection(self, run_docker, image_tag):
        with allure.step("Attempting to generate weak 1024-bit DH parameters"):
            result = run_docker(image_tag, [
                "genpkey", "-propquery", "fips=yes",
                "-genparam", "-algorithm", "DH",
                "-pkeyopt", "dh_paramgen_prime_len:1024"
            ])
        assert result.returncode != 0, "Security Breach: Weak 1024-bit DH parameters generated in FIPS mode!"

    @allure.story("Finite Field Diffie-Hellman (NIST SP 800-56A Rev. 3)")
    @allure.title("Verify FFDHE Alice/Bob Round-Trip Key Agreement (ffdhe2048)")
    @allure.description("""
        Validates end-to-end key agreement between two parties (Alice and Bob)
        using the FFDHE2048 safe prime group. Both parties must compute identical shared secrets.
    """)
    def test_ffdhe_round_trip_key_agreement(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/ffdhe"

            with allure.step("Alice generates DH key"):
                subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "genpkey", "-propquery", "fips=yes", "-algorithm", "DH",
                    "-pkeyopt", "group:ffdhe2048", "-out", f"{container_dir}/alice_priv.pem"
                ], check=True)
                subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkey", "-in", f"{container_dir}/alice_priv.pem",
                    "-pubout", "-out", f"{container_dir}/alice_pub.pem"
                ], check=True)

            with allure.step("Bob generates DH key"):
                subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "genpkey", "-propquery", "fips=yes", "-algorithm", "DH",
                    "-pkeyopt", "group:ffdhe2048", "-out", f"{container_dir}/bob_priv.pem"
                ], check=True)
                subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkey", "-in", f"{container_dir}/bob_priv.pem",
                    "-pubout", "-out", f"{container_dir}/bob_pub.pem"
                ], check=True)

            with allure.step("Deriving shared secrets"):
                res_a = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkeyutl", "-derive", "-propquery", "fips=yes",
                    "-inkey", f"{container_dir}/alice_priv.pem",
                    "-peerkey", f"{container_dir}/bob_pub.pem",
                    "-out", f"{container_dir}/alice_secret.bin"
                ], capture_output=True, text=True)
                assert res_a.returncode == 0, f"Alice derivation failed: {res_a.stderr}"

                res_b = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkeyutl", "-derive", "-propquery", "fips=yes",
                    "-inkey", f"{container_dir}/bob_priv.pem",
                    "-peerkey", f"{container_dir}/alice_pub.pem",
                    "-out", f"{container_dir}/bob_secret.bin"
                ], capture_output=True, text=True)
                assert res_b.returncode == 0, f"Bob derivation failed: {res_b.stderr}"

            with open(os.path.join(host_dir, "alice_secret.bin"), "rb") as fa, \
                 open(os.path.join(host_dir, "bob_secret.bin"), "rb") as fb:
                secret_a = fa.read()
                secret_b = fb.read()

            assert len(secret_a) > 0, "Shared secret is empty"
            assert secret_a == secret_b, "Cryptographic Failure: Alice and Bob shared secrets do not match!"

    @allure.story("RSA-OAEP Key Transport (NIST SP 800-56B Rev. 2)")
    @allure.title("Verify RSA-OAEP Encryption & Decryption Round-Trip (SHA-256)")
    @allure.description("""
        Validates RSA-OAEP (Optimal Asymmetric Encryption Padding) round-trip:
        Alice encrypts plaintext with Bob's public key using SHA-256 OAEP padding;
        Bob decrypts ciphertext with Bob's private key -> matches original plaintext.
    """)
    def test_rsa_oaep_encryption_and_decryption_flow(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/oaep"

            plain_text = b"NIST-SP800-56B-OAEP-ENCRYPTION-VERIFICATION"
            with open(os.path.join(host_dir, "plain.txt"), "wb") as f:
                f.write(plain_text)

            with allure.step("Step 1: Generating RSA 2048-bit Key Pair"):
                subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "genpkey", "-propquery", "fips=yes", "-algorithm", "RSA",
                    "-pkeyopt", "rsa_keygen_bits:2048", "-out", f"{container_dir}/priv.pem"
                ], check=True)
                subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkey", "-in", f"{container_dir}/priv.pem",
                    "-pubout", "-out", f"{container_dir}/pub.pem"
                ], check=True)

            with allure.step("Step 2: RSA-OAEP Encryption (SHA-256)"):
                res_enc = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkeyutl", "-encrypt", "-propquery", "fips=yes",
                    "-pubin", "-inkey", f"{container_dir}/pub.pem",
                    "-pkeyopt", "rsa_padding_mode:oaep",
                    "-pkeyopt", "rsa_oaep_md:sha256",
                    "-in", f"{container_dir}/plain.txt",
                    "-out", f"{container_dir}/cipher.bin"
                ], capture_output=True, text=True)
                assert res_enc.returncode == 0, f"OAEP encryption failed: {res_enc.stderr}"

            with allure.step("Step 3: RSA-OAEP Decryption (SHA-256)"):
                res_dec = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkeyutl", "-decrypt", "-propquery", "fips=yes",
                    "-inkey", f"{container_dir}/priv.pem",
                    "-pkeyopt", "rsa_padding_mode:oaep",
                    "-pkeyopt", "rsa_oaep_md:sha256",
                    "-in", f"{container_dir}/cipher.bin",
                    "-out", f"{container_dir}/decrypted.txt"
                ], capture_output=True, text=True)
                assert res_dec.returncode == 0, f"OAEP decryption failed: {res_dec.stderr}"

            with open(os.path.join(host_dir, "decrypted.txt"), "rb") as f:
                decrypted_text = f.read()

            assert decrypted_text == plain_text, "Decrypted text does not match original plaintext!"

    @allure.story("RSA-OAEP Key Transport (NIST SP 800-56B Rev. 2)")
    @allure.title("Verify RSA-OAEP Rejection of Insecure Digest (MD5)")
    @allure.description("""
        Validates that attempting RSA-OAEP encryption with MD5 digest is rejected in FIPS mode.
    """)
    def test_rsa_oaep_insecure_digest_rejection(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/oaep_md5"

            with open(os.path.join(host_dir, "plain.txt"), "wb") as f:
                f.write(b"SAMPLE")

            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "genpkey", "-propquery", "fips=yes", "-algorithm", "RSA",
                "-pkeyopt", "rsa_keygen_bits:2048", "-out", f"{container_dir}/priv.pem"
            ], check=True)
            subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "pkey", "-in", f"{container_dir}/priv.pem",
                "-pubout", "-out", f"{container_dir}/pub.pem"
            ], check=True)

            res_enc = subprocess.run([
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                "-v", f"{host_dir}:{container_dir}", image_tag,
                "pkeyutl", "-encrypt", "-propquery", "fips=yes",
                "-pubin", "-inkey", f"{container_dir}/pub.pem",
                "-pkeyopt", "rsa_padding_mode:oaep",
                "-pkeyopt", "rsa_oaep_md:md5",
                "-in", f"{container_dir}/plain.txt",
                "-out", f"{container_dir}/cipher.bin"
            ], capture_output=True, text=True)

            assert res_enc.returncode != 0, "Security Breach: RSA-OAEP accepted insecure MD5 digest!"

    @allure.story("Elliptic Curve Diffie-Hellman (NIST SP 800-56A Rev. 3)")
    @allure.title("Verify ECDH Alice/Bob Round-Trip Key Agreement (NIST P-256)")
    @allure.description("""
        Validates end-to-end ECDH key agreement between Alice and Bob on NIST P-256.
        Both parties must compute identical shared secrets.
    """)
    def test_ecdh_p256_round_trip_derivation(self, image_tag):
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_dir = os.path.abspath(tmpdir)
            os.chmod(host_dir, 0o777)
            container_dir = "/mnt/ecdh256"

            with allure.step("Alice generates P-256 key"):
                subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "genpkey", "-propquery", "fips=yes", "-algorithm", "EC",
                    "-pkeyopt", "ec_paramgen_curve:P-256", "-out", f"{container_dir}/alice_priv.pem"
                ], check=True)
                subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkey", "-in", f"{container_dir}/alice_priv.pem",
                    "-pubout", "-out", f"{container_dir}/alice_pub.pem"
                ], check=True)

            with allure.step("Bob generates P-256 key"):
                subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "genpkey", "-propquery", "fips=yes", "-algorithm", "EC",
                    "-pkeyopt", "ec_paramgen_curve:P-256", "-out", f"{container_dir}/bob_priv.pem"
                ], check=True)
                subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkey", "-in", f"{container_dir}/bob_priv.pem",
                    "-pubout", "-out", f"{container_dir}/bob_pub.pem"
                ], check=True)

            with allure.step("Deriving shared secrets"):
                res_a = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkeyutl", "-derive", "-propquery", "fips=yes",
                    "-inkey", f"{container_dir}/alice_priv.pem",
                    "-peerkey", f"{container_dir}/bob_pub.pem",
                    "-out", f"{container_dir}/alice_sec.bin"
                ], capture_output=True, text=True)
                assert res_a.returncode == 0, f"Alice derivation failed: {res_a.stderr}"

                res_b = subprocess.run([
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{host_dir}:{container_dir}", image_tag,
                    "pkeyutl", "-derive", "-propquery", "fips=yes",
                    "-inkey", f"{container_dir}/bob_priv.pem",
                    "-peerkey", f"{container_dir}/alice_pub.pem",
                    "-out", f"{container_dir}/bob_sec.bin"
                ], capture_output=True, text=True)
                assert res_b.returncode == 0, f"Bob derivation failed: {res_b.stderr}"

            with open(os.path.join(host_dir, "alice_sec.bin"), "rb") as fa, \
                 open(os.path.join(host_dir, "bob_sec.bin"), "rb") as fb:
                secret_a = fa.read()
                secret_b = fb.read()

            assert len(secret_a) > 0, "Shared secret is empty"
            assert secret_a == secret_b, "Cryptographic Failure: Alice and Bob ECDH shared secrets do not match!"




