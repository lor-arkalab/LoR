package tools

import (
	"crypto"
	crand "crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"math/rand"
)

func RandomIndexes(n, k int) (result []int) {
	rnd := make([]int, 0)
	result = append(result, rand.Intn(n))
	for i := 1; i < k; i++ {
		if len(rnd) == 0 {
			rnd = SHA256Arr(result)
		}
		result, rnd = append(result, rnd[0]%(n-i)), rnd[1:]
	}
	return
}

func GeneratePrivateKey(size int) (*rsa.PrivateKey, error) {
	privateKey, err := rsa.GenerateKey(crand.Reader, size)
	if err != nil {
		return nil, err
	}
	if err := privateKey.Validate(); err != nil {
		return nil, err
	}
	return privateKey, nil
}

func SignWithPrivateKey(data []byte, privateKey *rsa.PrivateKey) ([]byte, error) {
	hashed := sha256.Sum256(data)
	return rsa.SignPSS(crand.Reader, privateKey, crypto.SHA256, hashed[:], nil)
}

func VerifyWithPublicKey(data []byte, signature []byte, publicKey *rsa.PublicKey) error {
	hashed := sha256.Sum256(data)
	return rsa.VerifyPSS(publicKey, crypto.SHA256, hashed[:], signature, nil)
}

func SignWithPrivateKeyStr(data string, privateKey *rsa.PrivateKey) (string, error) {
	signature, err := SignWithPrivateKey([]byte(data), privateKey)
	if err != nil {
		return "", err
	}
	return string(signature), nil
}

func VerifyWithPublicKeyStr(data string, signature string, publicKey *rsa.PublicKey) error {
	return VerifyWithPublicKey([]byte(data), []byte(signature), publicKey)
}
