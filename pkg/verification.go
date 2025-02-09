package pkg

import (
	"errors"
	"slices"

	"golang.org/x/exp/rand"

	"github.com/Arka-Lab/LoR/tools"
)

const (
	VerificationMin = 21
	VerificationMax = 21
	BanCount        = 3
)

func (t *Trader) SubmitRing(ring *FractalRing) error {
	if err := t.validateFractalRing(ring); err != nil {
		validErrors := []string{"invalid selected cooperation ring", "invalid verification team", "invalid cooperation ring coins"}
		if !slices.Contains(validErrors, err.Error()) {
			return err
		}

		if t.Data.TraderType == BadVote || (t.Data.TraderType == RandomVote && rand.Float64() < BadBehavior) {
			return nil
		}
		return err
	}
	return t.Vote()
}

func (t *Trader) Vote() error {
	if t.Data.TraderType == BadVote || (t.Data.TraderType == RandomVote && rand.Float64() < BadBehavior) {
		return errors.New("bad behavior")
	}
	return nil
}

func selectRandomVerification(traders []string) (result []string) {
	if len(traders) < VerificationMin {
		return nil
	}

	randomIndices := tools.RandomIndexes(len(traders), rand.Intn(min(VerificationMax, len(traders))-VerificationMin+1)+VerificationMin)
	for _, index := range randomIndices {
		result = append(result, traders[index])
	}
	return
}

func selectVerificationTeam(traders []string, ring []string, firstOne string) (team []string) {
	k := VerificationMin + tools.SHA256Int(ring)%(VerificationMax-VerificationMin+1)
	if len(traders) < k {
		return nil
	}

	copiedTraders := make([]string, len(traders))
	copy(copiedTraders, traders)
	slices.Sort(copiedTraders)

	team = make([]string, k)
	if firstOne != "" {
		team[0] = firstOne
		for i := 0; i < len(copiedTraders); i++ {
			if copiedTraders[i] == firstOne {
				copiedTraders[i] = copiedTraders[0]
				copiedTraders = copiedTraders[1:]
				break
			}
		}
	} else {
		index := rand.Intn(len(traders))
		team[0] = copiedTraders[index]

		copiedTraders[index] = copiedTraders[0]
		copiedTraders = copiedTraders[1:]
	}

	rnd := make([]int, 0)
	for i := 1; i < k; i++ {
		if len(rnd) == 0 {
			rnd = tools.SHA256Arr(team)
		}
		index := rnd[0] % len(copiedTraders)
		team[i], rnd = copiedTraders[index], rnd[1:]

		copiedTraders[index] = copiedTraders[0]
		copiedTraders = copiedTraders[1:]
	}
	return
}
