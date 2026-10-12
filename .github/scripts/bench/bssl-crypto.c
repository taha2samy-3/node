#include <openssl/crypto.h>
#include <openssl/sha.h>
#include <openssl/evp.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#define CHUNK_SIZE 16384

static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(void) {
    double seconds = 1.0;
    char *env = getenv("BENCH_SECONDS");
    if (env) {
        double val = atof(env);
        if (val > 0.0) seconds = val;
    }

    unsigned char data[CHUNK_SIZE];
    memset(data, 0x5a, sizeof(data));

    // 1. SHA-256
    double start = get_time_sec();
    double end = start + seconds;
    unsigned long count = 0;
    unsigned char md[SHA256_DIGEST_LENGTH];
    while (get_time_sec() < end) {
        SHA256(data, sizeof(data), md);
        count++;
    }
    double elapsed = get_time_sec() - start;
    double sha256_mbs = (count * (double)CHUNK_SIZE) / elapsed / 1e6;

    // 2. SHA-512
    start = get_time_sec();
    end = start + seconds;
    count = 0;
    unsigned char md512[SHA512_DIGEST_LENGTH];
    while (get_time_sec() < end) {
        SHA512(data, sizeof(data), md512);
        count++;
    }
    elapsed = get_time_sec() - start;
    double sha512_mbs = (count * (double)CHUNK_SIZE) / elapsed / 1e6;

    // 3. AES-128-GCM
    start = get_time_sec();
    end = start + seconds;
    count = 0;
    unsigned char key128[16] = {0};
    unsigned char iv[12] = {0};
    unsigned char out[CHUNK_SIZE + 16];
    int outlen = 0;
    while (get_time_sec() < end) {
        EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
        EVP_EncryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, key128, iv);
        EVP_EncryptUpdate(ctx, out, &outlen, data, sizeof(data));
        EVP_EncryptFinal_ex(ctx, out, &outlen);
        EVP_CIPHER_CTX_free(ctx);
        count++;
    }
    elapsed = get_time_sec() - start;
    double aes128_mbs = (count * (double)CHUNK_SIZE) / elapsed / 1e6;

    // 4. AES-256-GCM
    start = get_time_sec();
    end = start + seconds;
    count = 0;
    unsigned char key256[32] = {0};
    while (get_time_sec() < end) {
        EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
        EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, key256, iv);
        EVP_EncryptUpdate(ctx, out, &outlen, data, sizeof(data));
        EVP_EncryptFinal_ex(ctx, out, &outlen);
        EVP_CIPHER_CTX_free(ctx);
        count++;
    }
    elapsed = get_time_sec() - start;
    double aes256_mbs = (count * (double)CHUNK_SIZE) / elapsed / 1e6;

    printf("[{\"name\":\"SHA-256\",\"metric\":\"MB/s\",\"value\":%.2f},"
           "{\"name\":\"SHA-512\",\"metric\":\"MB/s\",\"value\":%.2f},"
           "{\"name\":\"AES-128-GCM\",\"metric\":\"MB/s\",\"value\":%.2f},"
           "{\"name\":\"AES-256-GCM\",\"metric\":\"MB/s\",\"value\":%.2f}]\n",
           sha256_mbs, sha512_mbs, aes128_mbs, aes256_mbs);

    return 0;
}
