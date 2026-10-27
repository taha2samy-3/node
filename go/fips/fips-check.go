package main

import (
	"bytes"
	"crypto"
	"crypto/aes"
	"crypto/boring"
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
	// 0. Verify BoringCrypto is actually active at runtime
	if !boring.Enabled() {
		fatal("BoringCrypto is not active — binary was not built with GOEXPERIMENT=boringcrypto or CGO is disabled")
	}

	// 1. SHA-256 Known Answer Test (NIST FIPS 180-4 vector for "abc")
	//    Expected: ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
	katInput := []byte("abc")
	katExpected := "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
	got256 := fmt.Sprintf("%x", sha256.Sum256(katInput))
	if got256 != katExpected {
		fatal("SHA-256 KAT mismatch: got %s, want %s", got256, katExpected)
	}

	// 2. SHA-512 Known Answer Test (NIST FIPS 180-4 vector for "abc")
	//    Expected: ddaf35a193617aba...
	kat512Expected := "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f"
	got512 := fmt.Sprintf("%x", sha512.Sum512(katInput))
	if got512 != kat512Expected {
		fatal("SHA-512 KAT mismatch: got %s, want %s", got512, kat512Expected)
	}

	// 3. AES-256-GCM round-trip
	msg := []byte("fips 140-3 validation vector")
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

	// 4. RSA-2048 sign/verify
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

	// 5. ECDSA P-256 sign/verify
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

	fmt.Printf("FIPS check passed: Go %s (%s/%s), BoringCrypto active, KATs verified\n",
		runtime.Version(), runtime.GOOS, runtime.GOARCH)
}
