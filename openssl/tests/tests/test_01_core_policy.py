import pytest
import allure
import re
import subprocess
import tempfile
import os
@allure.feature("FIPS 140-3 Core Policy & Integrity")
class TestCorePolicyAndIntegrity:
    """
    This suite validates the fundamental operational health of the FIPS module.
    It covers:
    1. Module Integrity (Checksums/POST).
    2. Global Policy Enforcement (fips=yes).
    3. Cryptographic Boundaries (Key lengths, Tag lengths).
    4. Algorithm Retirement (Triple-DES, SHA-1).
    5. Service Indicators (Active Status).
    """




    @allure.story("Mandatory Approved Mode Conditions")
    @allure.title("Verify FIPS Config File Indicators (fipsmodule.cnf)")
    @allure.description("""
        Validates that the mandatory FIPS 140-3 indicators are correctly written 
        into the fipsmodule.cnf file. This ensures the module was installed 
        with the correct security flags as per Security Policy Page 10.
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("config", "fipsmodule.cnf", "audit")
    def test_fips_config_file_indicators(self, image_tag):
        container_config_path = "/usr/local/ssl/fipsmodule.cnf"
        
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            host_path = os.path.abspath(os.path.join(tmpdir, "fips_check.cnf"))
            
            with allure.step("Extracting fipsmodule.cnf from container via volume mount"):
                copy_cmd = [
                    "docker", "run", "--rm",
                    "-v", f"{os.path.abspath(tmpdir)}:/mnt_out",
                    "--entrypoint", "cp", 
                    image_tag,
                    container_config_path, "/mnt_out/fips_check.cnf"
                ]
                
                subprocess.run(["docker", "create", "--name", "fips_temp", image_tag], check=True)
                subprocess.run(["docker", "cp", f"fips_temp:{container_config_path}", host_path], check=True)
                subprocess.run(["docker", "rm", "fips_temp"], check=True)

            with open(host_path, "r") as f:
                config_content = f.read()
                allure.attach(config_content, name="fipsmodule.cnf Content")

        with allure.step("Auditing mandatory indicators in the config file"):
            # المؤشرات المطلوبة في صفحة 10
            required_settings = {
                "security-checks": "1",
                "conditional-errors": "1",
                "drbg-no-trunc-md": "1",
                "tls1-prf-ems-check": "1"
            }

            print("\n" + "="*50)
            print("fipsmodule.cnf AUDIT RESULTS:")
            print("="*50)

            missing_or_wrong = []
            for key, val in required_settings.items():
                expected_line = f"{key} = {val}"
                if expected_line in config_content:
                    print(f"Indicator: {key:<20} | Status: FOUND (Value 1)")
                    allure.dynamic.parameter(f"Config: {key}", "Verified (1)")
                else:
                    print(f"Indicator: {key:<20} | Status: MISSING OR WRONG")
                    missing_or_wrong.append(key)
            
            print("="*50 + "\n")

            if missing_or_wrong:
                pytest.fail(f"Compliance Failure: Mandatory settings {missing_or_wrong} are not correctly set in fipsmodule.cnf. See PDF Page 10.")

        with allure.step("FIPS configuration file is compliant"):
            allure.dynamic.parameter("Result", "All Indicators Present in File")









    @allure.story("Integrity")
    @allure.title("Verify FIPS Module Version & Metadata")
    @allure.description("""
        Ensures the loaded FIPS provider matches the expected NIST-validated version 
        (e.g., 3.1.2) and correctly identifies itself as 'OpenSSL FIPS Provider'.
    """)
    @allure.severity(allure.severity_level.NORMAL)
    def test_provider_version_metadata(self, run_docker, image_tag):
        with allure.step("Fetching detailed provider metadata"):
            result = run_docker(image_tag, ["list", "-providers", "-verbose"])
            allure.attach(result.stdout, name="Full Metadata Output", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Validating provider identity"):
            assert result.returncode == 0, "Failed to retrieve provider list."
            assert "name: OpenSSL FIPS Provider" in result.stdout, \
                "Provider identity mismatch: 'OpenSSL FIPS Provider' not found in metadata."

        with allure.step("Verifying NIST-validated version"):
            expected_version = "version: 3.1.2"
            assert expected_version in result.stdout, \
                f"Version mismatch: Expected '{expected_version}' to comply with certification."

        with allure.step("Recording compliance details"):
            allure.dynamic.parameter("Validated Version", "3.1.2")
            allure.dynamic.parameter("Provider Name", "OpenSSL FIPS Provider")

    @allure.story("Integrity & Tamper Resistance")
    @allure.title("Verify FIPS Provider Rejection on Configuration Tampering")
    @allure.description("""
        Simulates an unauthorized tampering attack on the FIPS cryptographic module:
        1. Extracts fipsmodule.cnf from the container via openssl base64.
        2. Deliberately corrupts the 'module-mac' checksum value.
        3. Mounts the tampered configuration back into the container.
        4. Validates that the FIPS provider's power-up integrity self-test detects
           the violation and strictly refuses to enter the 'active' operational state.
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("integrity", "tamper-detection", "module-mac", "self-test")
    def test_integrity_check_tampering(self, image_tag):
        target_path = "/usr/local/ssl/fipsmodule.cnf"

        with allure.step("Extracting and decoding FIPS module configuration via OpenSSL"):
            extract_cmd = [
                "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                image_tag, "base64", "-in", target_path
            ]
            result = subprocess.run(extract_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Failed to extract configuration: {result.stderr}"
            import base64
            original_content = base64.b64decode(result.stdout).decode("utf-8")

        with allure.step("Injecting corrupted MAC to simulate unauthorized modification"):
            assert "module-mac =" in original_content, "Could not locate 'module-mac' in fipsmodule.cnf"
            corrupted_mac = "00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00"
            corrupted_content = re.sub(r"(module-mac\s*=\s*)[0-9a-fA-F:]+", r"\g<1>" + corrupted_mac, original_content)
            allure.attach(corrupted_content, name="Corrupted Config Preview", attachment_type=allure.attachment_type.TEXT)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(corrupted_content)
            temp_config_path = f.name

        try:
            with allure.step("Verifying provider status with corrupted MAC"):
                test_cmd = [
                    "docker", "run", "--user", "0", "--rm", "--entrypoint", "/usr/local/bin/openssl",
                    "-v", f"{temp_config_path}:{target_path}",
                    image_tag, "list", "-providers", "-verbose"
                ]
                final_check = subprocess.run(test_cmd, capture_output=True, text=True)
                allure.attach(final_check.stdout, name="Module Status Output")
                allure.attach(final_check.stderr, name="Integrity Error Logs")

                is_fips_active = "fips" in final_check.stdout.lower() and "status: active" in final_check.stdout.lower()
                assert not is_fips_active, "Security Breach: FIPS module entered 'active' state despite tampered MAC!"
        finally:
            if os.path.exists(temp_config_path):
                os.remove(temp_config_path)

        with allure.step("Tamper resistance verified"):
            allure.dynamic.parameter("Tampered Field", "module-mac")
            allure.dynamic.parameter("System Response", "Module Load Rejected (Inactive)")

    # ==========================================================================
    # SECTION 2: GLOBAL POLICY ENFORCEMENT (Files: 9, 20)
    # ==========================================================================

    @allure.story("Global Configuration Enforcement")
    @allure.title("Verify Mandatory FIPS Property Enforcement")
    @allure.description("""
        Tests the strict enforcement of the FIPS security policy.
        Attempts to bypass FIPS mode using '-propquery fips=no'. 
        The system MUST reject this request if 'default_properties = fips=yes' 
        is correctly configured in the OpenSSL configuration file.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("security", "bypass-attempt")
    def test_mandatory_fips_property(self, run_docker, image_tag):
        with allure.step("Attempting to bypass FIPS policy using restricted property query"):
            result = run_docker(image_tag, ["dgst", "-sha256", "-propquery", "fips=no", "/dev/null"])
            
            allure.attach(result.stdout, name="Stdout", attachment_type=allure.attachment_type.TEXT)
            allure.attach(result.stderr, name="Stderr", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying that the system rejected the non-FIPS request"):
            error_msg = result.stderr.lower()
            
            if result.returncode == 0:
                allure.dynamic.status_details(message="Security Bypass Detected: Non-FIPS properties were accepted.")
                pytest.fail("Compliance Failure: The system allowed a non-FIPS property query (fips=no).")

            assert any(x in error_msg for x in ["unsupported", "fetch failed", "error"]), \
                f"Unexpected error message during bypass attempt: {result.stderr}"

        with allure.step("Policy enforcement confirmed"):
            allure.dynamic.parameter("Enforcement Strategy", "default_properties = fips=yes")














   
   
   
   
   
   
   
   
   
   
   

    @allure.story("Operational Stability")
    @allure.title("Verify FIPS Module Operational State Persistence")
    @allure.description("""
        Validates the operational stability of the FIPS module as required by FIPS 140-3 standards.
        This test ensures that the cryptographic module remains in a consistent 'active' state 
        during service requests and does not transition into an undefined, uninitialized, 
        or insecure error state during standard operations.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("operational-stability", "state-machine", "compliance")
    def test_operational_state_stability(self, run_docker, image_tag):
        with allure.step("Checking module operational status and service availability"):
            result = run_docker(image_tag, ["list", "-providers", "-verbose"])
            
            allure.attach(result.stdout, name="Operational Status Output", attachment_type=allure.attachment_type.TEXT)
            allure.attach(result.stderr, name="Standard Error Output", attachment_type=allure.attachment_type.TEXT)

            assert result.returncode == 0, "The module failed to respond to service requests, indicating operational instability."
            
        with allure.step("Verifying persistence of the 'active' state"):
            output_lower = result.stdout.lower()
            assert "status: active" in output_lower, \
                "Module operational state is not 'active'. The module may have entered an error or maintenance state."

        with allure.step("Monitoring for unauthorized state transitions or fatal errors"):
            error_msg = result.stderr.lower()
            # FIPS 140-3 modules must halt or report if a fatal error state is reached
            fatal_indicators = ["error state", "fatal error", "panic", "self-test failed", "module terminated"]
            
            assert not any(indicator in error_msg for indicator in fatal_indicators), \
                f"Critical operational failure detected. Module reported a fatal state: {result.stderr}"

        with allure.step("Operational state machine validation confirmed"):
            allure.dynamic.parameter("Observed State", "Active")
            allure.dynamic.parameter("State Transition Integrity", "Verified")



    @allure.story("Provider Isolation")
    @allure.title("Verify Default Provider Blocking (Isolation Check)")
    @allure.description("""
        Ensures strict isolation between the FIPS provider and the default provider.
        By attempting to call an unapproved algorithm (MD5) without explicit property queries,
        this test verifies that the default provider is disabled or inaccessible. 
        This prevents accidental usage of non-validated cryptographic implementations.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("security", "provider-isolation", "compliance")
    def test_default_provider_isolation(self, run_docker, image_tag):
        with allure.step("Attempting to call MD5 without explicit provider selection"):
            result = run_docker(image_tag, ["dgst", "-md5", "/dev/null"])
            
            allure.attach(result.stdout, name="Stdout Output", attachment_type=allure.attachment_type.TEXT)
            allure.attach(result.stderr, name="Stderr Output", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Verifying mandatory algorithm rejection"):
            if result.returncode == 0:
                allure.dynamic.status_details(message="Security Leak: Non-FIPS algorithms are still accessible via the Default Provider.")
                pytest.fail("Compliance Failure: The system allowed MD5 execution, indicating the Default Provider is still active.")

            error_msg = result.stderr.lower()
            assert any(x in error_msg for x in ["unsupported", "fetch failed", "error", "not found"]), \
                f"Unexpected behavior during isolation check: {result.stderr}"

        with allure.step("Provider isolation successfully verified"):
            allure.dynamic.parameter("Tested Algorithm", "MD5 (Non-Approved)")
            allure.dynamic.parameter("Isolation Status", "Strictly Enforced")

    @allure.story("Provider Isolation")
    @allure.title("Verify Default Provider is Completely Unloaded")
    @allure.description("""
        Validates that the 'default' provider is not loaded in OpenSSL configuration.
        Only the FIPS provider ('fips') and the auxiliary Base provider ('base')
        must be present in active providers list.
    """)
    def test_default_provider_strictly_unloaded(self, run_docker, image_tag):
        result = run_docker(image_tag, ["list", "-providers"])
        assert result.returncode == 0, f"Failed to list providers: {result.stderr}"
        stdout = result.stdout.lower()
        assert "default" not in stdout.split(), f"Architecture Violation: Default provider is loaded: {result.stdout}"
        assert "fips" in stdout, "Missing FIPS provider in provider list"

    @allure.story("FIPS 140-3 Service Indicators")
    @allure.title("Verify FIPS Provider Gettable Parameter Indicators")
    @allure.description("""
        Validates that the FIPS provider exports mandatory indicator parameters:
        security-checks, tls1-prf-ems-check, and drbg-no-trunc-md as per FIPS 140-3 policy.
    """)
    def test_fips_provider_gettable_parameters(self, run_docker, image_tag):
        result = run_docker(image_tag, ["list", "-providers", "-verbose"])
        assert result.returncode == 0, f"Failed to list providers: {result.stderr}"
        out = result.stdout.lower()
        mandatory_params = ["security-checks", "tls1-prf-ems-check", "drbg-no-trunc-md"]
        for param in mandatory_params:
            assert param in out, f"FIPS parameter indicator missing: {param}"