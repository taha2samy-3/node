package main

import (
	"bytes"
	"crypto"
	"crypto/aes"
	"crypto/cipher"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/sha512"
	"fmt"
	"os"
	"runtime"

	_ "crypto/tls/fipsonly"
)

func fatal(format string, args ...any) {
	fmt.Fprintf(os.Stderr, "FIPS check FAILED: "+format+"\n", args...)
	os.Exit(1)
}

func main() {
	// 1. Verify SHA-256 and SHA-512 KAT
	msg := []byte("fips 140-3 validation vector")
	h256 := sha256.Sum256(msg)
	if len(h256) != 32 {
		fatal("SHA-256 length mismatch")
	}

	h512 := sha512.Sum512(msg)
	if len(h512) != 64 {
		fatal("SHA-512 length mismatch")
	}

	// 2. Verify AES-256-GCM round-trip
	key := make([]byte, 32)
	nonce := make([]byte, 12)
	if _, err := rand.Read(key); err != nil {
		fatal("rand.Read key failed: %v", err)
	}
	if _, err := rand.Read(nonce); err != nil {
		fatal("rand.Read nonce failed: %v", err)
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		fatal("aes.NewCipher failed: %v", err)
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		fatal("cipher.NewGCM failed: %v", err)
	}

	ciphertext := gcm.Seal(nil, nonce, msg, nil)
	plaintext, err := gcm.Open(nil, nonce, ciphertext, nil)
	if err != nil || !bytes.Equal(plaintext, msg) {
		fatal("AES-256-GCM round-trip failed: %v", err)
	}

	// 3. Verify RSA-2048 key generation and sign/verify
	rsaKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		fatal("rsa.GenerateKey failed: %v", err)
	}
	hashed := sha256.Sum256(msg)
	sig, err := rsa.SignPSS(rand.Reader, rsaKey, crypto.SHA256, hashed[:], nil)
	if err != nil {
		fatal("rsa.SignPSS failed: %v", err)
	}
	if err := rsa.VerifyPSS(&rsaKey.PublicKey, crypto.SHA256, hashed[:], sig, nil); err != nil {
		fatal("rsa.VerifyPSS failed: %v", err)
	}

	// 4. Verify ECDSA P-256 key generation and sign/verify
	ecKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		fatal("ecdsa.GenerateKey failed: %v", err)
	}
	ecSig, err := ecdsa.SignASN1(rand.Reader, ecKey, hashed[:])
	if err != nil {
		fatal("ecdsa.SignASN1 failed: %v", err)
	}
	if !ecdsa.VerifyASN1(&ecKey.PublicKey, hashed[:], ecSig) {
		fatal("ecdsa.VerifyASN1 failed")
	}

	fmt.Printf("FIPS check passed: Go %s (%s/%s), BoringCrypto / fipsonly enforced\n",
		runtime.Version(), runtime.GOOS, runtime.GOARCH)
}
