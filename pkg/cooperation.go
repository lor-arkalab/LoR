package pkg

import (
	"errors"
	"reflect"
	"slices"

	"github.com/Arka-Lab/LoR/tools"
	"golang.org/x/exp/rand"
)

const (
	RoundsCount = 10
	RoundLength = 1000
)

type CooperationTable struct {
	ID       string  `json:"id"`
	Weight   float64 `json:"weight"`
	Next     string  `json:"next"`
	Prev     string  `json:"prev"`
	Investor string  `json:"investor"`

	UnusedCoins [][]string `json:"-"`
	CoinIDs     []string
	FractalID   string
	IsValid     bool
	Rounds      int
}

func (t *Trader) checkForCooperationRing() *CooperationTable {
	unusedCoins := make([][]string, t.Data.CoinTypeCount)
	for _, coin := range t.Data.Coins {
		if coin.Prev == "" && coin.Next == "" {
			unusedCoins[coin.Type] = append(unusedCoins[coin.Type], coin.ID)
		}
	}

	for _, coins := range unusedCoins {
		if len(coins) == 0 {
			return nil
		}
	}

	isValid := true
	var selectedCoins []string
	selectedCoins = selectCooperationRing(unusedCoins, "")

	cooperationID := tools.SHA256Str(selectedCoins)
	for i, coinID := range selectedCoins {
		coin := t.Data.Coins[coinID]
		coin.CooperationID = cooperationID
		coin.Next = selectedCoins[(i+1)%len(selectedCoins)]
		coin.Prev = selectedCoins[(i-1+len(selectedCoins))%len(selectedCoins)]
		t.Data.Coins[coinID] = coin
	}

	return &CooperationTable{
		ID:          cooperationID,
		Weight:      t.calculateWeight(selectedCoins),
		Investor:    selectedCoins[0],
		CoinIDs:     selectedCoins,
		UnusedCoins: unusedCoins,
		IsValid:     isValid,
		Rounds:      -1,
	}
}

func (t *Trader) calculateWeight(ring []string) (weight float64) {
	for _, coinID := range ring[1:] {
		weight += t.Data.Coins[coinID].Amount
	}
	return
}

func (t *Trader) validateCooperationRing(cooperation CooperationTable) error {
	if cooperation.ID != tools.SHA256Str(cooperation.CoinIDs) {
		return errors.New("invalid cooperation ring id")
	} else if cooperation.Weight != t.calculateWeight(cooperation.CoinIDs) {
		return errors.New("invalid cooperation ring weight")
	} else if cooperation.Investor != cooperation.CoinIDs[0] {
		return errors.New("invalid cooperation ring investor")
	}

	for i, coinID := range cooperation.CoinIDs {
		if coin, ok := t.Data.Coins[coinID]; !ok {
			return errors.New("coin not found")
		} else if coin.Status != Run {
			return errors.New("invalid coin status")
		} else if coin.Type != uint(i) {
			return errors.New("invalid coin type")
		}
	}

	expectedRing := selectCooperationRing(cooperation.UnusedCoins, cooperation.Investor)
	if !reflect.DeepEqual(expectedRing, cooperation.CoinIDs) {
		return errors.New("invalid cooperation ring coins")
	}
	return nil
}

func selectRandomCooperation(unusedCoins [][]string) []string {
	selectedRing := make([]string, len(unusedCoins))
	for i := 0; i < len(unusedCoins); i++ {
		selectedRing[i] = unusedCoins[i][rand.Intn(len(unusedCoins[i]))]
	}
	return selectedRing
}

func selectCooperationRing(unusedCoins [][]string, investor string) []string {
	rnd := make([]int, 0)
	selectedRing := make([]string, len(unusedCoins))
	if investor == "" {
		selectedRing[0] = unusedCoins[0][rand.Intn(len(unusedCoins[0]))]
	} else {
		selectedRing[0] = investor
	}
	for i := 1; i < len(unusedCoins); i++ {
		if len(rnd) == 0 {
			rnd = tools.SHA256Arr(selectedRing)
		}
		slices.Sort(unusedCoins[i])
		rnd, selectedRing[i] = rnd[1:], unusedCoins[i][rnd[0]%len(unusedCoins[i])]
	}
	return selectedRing
}

func (t *Trader) ExpireRing(ring CooperationTable) {
	for _, coinID := range ring.CoinIDs {
		coin := t.Data.Coins[coinID]
		coin.Status = Expired
		t.Data.Coins[coinID] = coin
	}
}

func (t *Trader) PayRing(ring CooperationTable) {
	for _, coinID := range ring.CoinIDs {
		coin := t.Data.Coins[coinID]
		coin.Status = Paid
		t.Data.Coins[coinID] = coin
	}
}
