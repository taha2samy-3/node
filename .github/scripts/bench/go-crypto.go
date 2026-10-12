package main

import (
	"crypto"
	"crypto/aes"
	"crypto/cipher"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/hmac"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/sha512"
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"time"
)

type Result struct {
	Name   string  `json:"name"`
	Metric string  `json:"metric"`
	Value  float64 `json:"value"`
}

func measure(seconds float64, fn func(), byteCount int) float64 {
	duration := time.Duration(seconds * float64(time.Second))
	start := time.Now()
	end := start.Add(duration)
	count := 0
	for time.Now().Before(end) {
		fn()
		count++
	}
	elapsed := time.Since(start).Seconds()
	if byteCount > 0 {
		return (float64(count) * float64(byteCount)) / elapsed / 1e6
	}
	return float64(count) / elapsed
}

func main() {
	secs := 1.0
	if env := os.Getenv("BENCH_SECONDS"); env != "" {
		if v, err := strconv.ParseFloat(env, 64); err == nil && v > 0 {
			secs = v
		}
	}

	data := make([]byte, 16384)
	key := make([]byte, 32)
	nonce := make([]byte, 12)
	rand.Read(data)
	rand.Read(key)
	rand.Read(nonce)

	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err)
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		panic(err)
	}

	ecKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		panic(err)
	}
	rsaKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		panic(err)
	}

	h256 := sha256.Sum256(data)
	ecSig, err := ecdsa.SignASN1(rand.Reader, ecKey, h256[:])
	if err != nil {
		panic(err)
	}
	rsaSig, err := rsa.SignPSS(rand.Reader, rsaKey, crypto.SHA256, h256[:], nil)
	if err != nil {
		panic(err)
	}

	var results []Result

	// SHA-256
	results = append(results, Result{
		Name:   "SHA-256",
		Metric: "MB/s",
		Value: measure(secs, func() {
			_ = sha256.Sum256(data)
		}, len(data)),
	})

	// SHA-512
	results = append(results, Result{
		Name:   "SHA-512",
		Metric: "MB/s",
		Value: measure(secs, func() {
			_ = sha512.Sum512(data)
		}, len(data)),
	})

	// HMAC-SHA256
	results = append(results, Result{
		Name:   "HMAC-SHA256",
		Metric: "MB/s",
		Value: measure(secs, func() {
			mac := hmac.New(sha256.New, key)
			mac.Write(data)
			_ = mac.Sum(nil)
		}, len(data)),
	})

	// AES-256-GCM
	results = append(results, Result{
		Name:   "AES-256-GCM encrypt",
		Metric: "MB/s",
		Value: measure(secs, func() {
			_ = gcm.Seal(nil, nonce, data, nil)
		}, len(data)),
	})

	// ECDSA P-256 sign
	results = append(results, Result{
		Name:   "ECDSA P-256 sign",
		Metric: "ops/s",
		Value: measure(secs, func() {
			_, _ = ecdsa.SignASN1(rand.Reader, ecKey, h256[:])
		}, 0),
	})

	// ECDSA P-256 verify
	results = append(results, Result{
		Name:   "ECDSA P-256 verify",
		Metric: "ops/s",
		Value: measure(secs, func() {
			_ = ecdsa.VerifyASN1(&ecKey.PublicKey, h256[:], ecSig)
		}, 0),
	})

	// RSA-2048 sign
	results = append(results, Result{
		Name:   "RSA-2048 sign",
		Metric: "ops/s",
		Value: measure(secs, func() {
			_, _ = rsa.SignPSS(rand.Reader, rsaKey, crypto.SHA256, h256[:], nil)
		}, 0),
	})

	// RSA-2048 verify
	results = append(results, Result{
		Name:   "RSA-2048 verify",
		Metric: "ops/s",
		Value: measure(secs, func() {
			_ = rsa.VerifyPSS(&rsaKey.PublicKey, crypto.SHA256, h256[:], rsaSig, nil)
		}, 0),
	})

	out, _ := json.Marshal(results)
	fmt.Println(string(out))
}
