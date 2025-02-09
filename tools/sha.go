package tools

import (
	"encoding/hex"
	"fmt"

	"golang.org/x/crypto/sha3"
)

func SHA256(data interface{}) []byte {
	h := sha3.New256()
	h.Write([]byte(fmt.Sprint(data)))
	return h.Sum(nil)
}

func SHA256Str(data interface{}) string {
	return hex.EncodeToString(SHA256(data))
}

func SHA256Arr(data interface{}) []int {
	result := make([]int, 8)
	for index, c := range SHA256(data) {
		result[index/4] ^= int(c) << (index % 4 << 3)
	}
	return result
}

func SHA256Int(data interface{}) int {
	var result int
	for _, c := range SHA256Arr(data) {
		result ^= c
	}
	return result
}
