#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <openssl/crypto.h>
#include <openssl/aead.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>

static int test_aes_gcm(size_t key_len) {
    const EVP_AEAD *aead = (key_len == 16) ? EVP_aead_aes_128_gcm() : EVP_aead_aes_256_gcm();
    uint8_t key[32] = {0};
    uint8_t nonce[12] = {0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c};
    uint8_t plain[] = "BoringCrypto FIPS 140-3 Known Answer Test Payload";
    uint8_t cipher[128];
    size_t cipher_len = 0;

    memset(key, 0x42, key_len);

    EVP_AEAD_CTX ctx;
    if (!EVP_AEAD_CTX_init(&ctx, aead, key, key_len, 16, NULL)) {
        return 0;
    }
    if (!EVP_AEAD_CTX_seal(&ctx, cipher, &cipher_len, sizeof(cipher),
                           nonce, sizeof(nonce), plain, sizeof(plain), NULL, 0)) {
        EVP_AEAD_CTX_cleanup(&ctx);
        return 0;
    }

    uint8_t decrypted[128];
    size_t dec_len = 0;
    if (!EVP_AEAD_CTX_open(&ctx, decrypted, &dec_len, sizeof(decrypted),
                           nonce, sizeof(nonce), cipher, cipher_len, NULL, 0)) {
        EVP_AEAD_CTX_cleanup(&ctx);
        return 0;
    }
    EVP_AEAD_CTX_cleanup(&ctx);

    return (dec_len == sizeof(plain) && memcmp(plain, decrypted, sizeof(plain)) == 0);
}

static int test_aes_gcm_tamper(void) {
    const EVP_AEAD *aead = EVP_aead_aes_256_gcm();
    uint8_t key[32];
    uint8_t nonce[12] = {1,2,3,4,5,6,7,8,9,10,11,12};
    uint8_t plain[] = "Sensitive Cryptographic Data";
    uint8_t cipher[128];
    size_t cipher_len = 0;

    memset(key, 0x55, sizeof(key));

    EVP_AEAD_CTX ctx;
    if (!EVP_AEAD_CTX_init(&ctx, aead, key, sizeof(key), 16, NULL)) return 0;
    if (!EVP_AEAD_CTX_seal(&ctx, cipher, &cipher_len, sizeof(cipher),
                           nonce, sizeof(nonce), plain, sizeof(plain), NULL, 0)) {
        EVP_AEAD_CTX_cleanup(&ctx);
        return 0;
    }

    // Tamper with the authentication tag at the end
    cipher[cipher_len - 1] ^= 0x01;

    uint8_t decrypted[128];
    size_t dec_len = 0;
    int open_ok = EVP_AEAD_CTX_open(&ctx, decrypted, &dec_len, sizeof(decrypted),
                                    nonce, sizeof(nonce), cipher, cipher_len, NULL, 0);
    EVP_AEAD_CTX_cleanup(&ctx);

    // open_ok must be 0 (tampering rejected)
    return (open_ok == 0);
}

static int test_hmac_sha256(void) {
    const uint8_t key[] = "Jefe";
    const uint8_t data[] = "what do ya want for nothing?";
    // RFC 4231 Test Case 2 HMAC-SHA256: 5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843
    uint8_t expected[32] = {
        0x5b, 0xdc, 0xc1, 0x46, 0xbf, 0x60, 0x75, 0x4e,
        0x6a, 0x04, 0x24, 0x26, 0x08, 0x95, 0x75, 0xc7,
        0x5a, 0x00, 0x3f, 0x08, 0x9d, 0x27, 0x39, 0x83,
        0x9d, 0xec, 0x58, 0xb9, 0x64, 0xec, 0x38, 0x43
    };

    uint8_t out[32];
    unsigned int out_len = 0;
    if (!HMAC(EVP_sha256(), key, sizeof(key) - 1, data, sizeof(data) - 1, out, &out_len)) {
        return 0;
    }
    return (out_len == 32 && memcmp(out, expected, 32) == 0);
}

static int test_hmac_sha512(void) {
    const uint8_t key[] = "Jefe";
    const uint8_t data[] = "what do ya want for nothing?";
    // RFC 4231 Test Case 2 HMAC-SHA512:
    // 164b7a7bfcf819e2e395fbe73b56e0a387bd64222e831fd610270cd7ea2505549758bf75c05a994a6d034f65f8f0e6fdcaeab1a34d4a6b4b636e070a38bce737
    uint8_t expected[64] = {
        0x16, 0x4b, 0x7a, 0x7b, 0xfc, 0xf8, 0x19, 0xe2,
        0xe3, 0x95, 0xfb, 0xe7, 0x3b, 0x56, 0xe0, 0xa3,
        0x87, 0xbd, 0x64, 0x22, 0x2e, 0x83, 0x1f, 0xd6,
        0x10, 0x27, 0x0c, 0xd7, 0xea, 0x25, 0x05, 0x54,
        0x97, 0x58, 0xbf, 0x75, 0xc0, 0x5a, 0x99, 0x4a,
        0x6d, 0x03, 0x4f, 0x65, 0xf8, 0xf0, 0xe6, 0xfd,
        0xca, 0xea, 0xb1, 0xa3, 0x4d, 0x4a, 0x6b, 0x4b,
        0x63, 0x6e, 0x07, 0x0a, 0x38, 0xbc, 0xe7, 0x37
    };

    uint8_t out[64];
    unsigned int out_len = 0;
    if (!HMAC(EVP_sha512(), key, sizeof(key) - 1, data, sizeof(data) - 1, out, &out_len)) {
        return 0;
    }
    return (out_len == 64 && memcmp(out, expected, 64) == 0);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <command>\n", argv[0]);
        return 1;
    }

    const char *cmd = argv[1];

    if (strcmp(cmd, "fips_mode") == 0) {
        printf("%d\n", FIPS_mode());
        return 0;
    }

    if (strcmp(cmd, "fips_mode_set_zero") == 0) {
        int set_res = FIPS_mode_set(0);
        int mode_after = FIPS_mode();
        // FIPS_mode_set(0) must return 0, and FIPS_mode() must remain 1
        if (set_res == 0 && mode_after == 1) {
            printf("BLOCKED\n");
            return 0;
        }
        printf("FAILED\n");
        return 1;
    }

    if (strcmp(cmd, "self_test") == 0) {
        printf("%d\n", BORINGSSL_self_test());
        return 0;
    }

    if (strcmp(cmd, "self_test_all") == 0) {
        printf("%d\n", BORINGSSL_self_test_all());
        return 0;
    }

    if (strcmp(cmd, "module_name") == 0) {
        const char *name = FIPS_module_name();
        printf("%s\n", name ? name : "UNKNOWN");
        return 0;
    }

    if (strcmp(cmd, "module_hash") == 0) {
        const uint8_t *hash = FIPS_module_hash();
        if (!hash) {
            printf("NULL\n");
            return 1;
        }
        for (int i = 0; i < 32; i++) {
            printf("%02x", hash[i]);
        }
        printf("\n");
        return 0;
    }

    if (strcmp(cmd, "query_aes_gcm") == 0) {
        printf("%d\n", FIPS_query_algorithm_status("AES-GCM"));
        return 0;
    }

    if (strcmp(cmd, "aes_128_gcm") == 0) {
        if (test_aes_gcm(16)) {
            printf("OK\n");
            return 0;
        }
        printf("FAIL\n");
        return 1;
    }

    if (strcmp(cmd, "aes_256_gcm") == 0) {
        if (test_aes_gcm(32)) {
            printf("OK\n");
            return 0;
        }
        printf("FAIL\n");
        return 1;
    }

    if (strcmp(cmd, "aes_gcm_tamper") == 0) {
        if (test_aes_gcm_tamper()) {
            printf("REJECTED\n");
            return 0;
        }
        printf("ACCEPTED_UNEXPECTEDLY\n");
        return 1;
    }

    if (strcmp(cmd, "hmac_sha256") == 0) {
        if (test_hmac_sha256()) {
            printf("OK\n");
            return 0;
        }
        printf("FAIL\n");
        return 1;
    }

    if (strcmp(cmd, "hmac_sha512") == 0) {
        if (test_hmac_sha512()) {
            printf("OK\n");
            return 0;
        }
        printf("FAIL\n");
        return 1;
    }

    fprintf(stderr, "Unknown command: %s\n", cmd);
    return 1;
}
