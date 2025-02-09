package pkg

import (
	"crypto/rsa"
	"errors"
	"strconv"
	"time"

	"github.com/Arka-Lab/LoR/tools"
)

const (
	KeySize = 2048
)

var (
	BadBehavior = 0.1
)

type BehaviorType int

const (
	Normal BehaviorType = iota
	RandomVote
	BadVote
)

type TraderData struct {
	TraderType    BehaviorType
	CoinTypeCount uint
	Ticker        *time.Ticker
	PrivateKey    *rsa.PrivateKey
	Traders       map[string]Trader
	Coins         map[string]CoinTable
	Cooperations  map[string]CooperationTable
	BanUntil      int
}

type Trader struct {
	ID        string         `json:"id"`
	Account   float64        `json:"account"`
	Wallet    string         `json:"wallet"`
	PublicKey *rsa.PublicKey `json:"public_key"`

	Data *TraderData `json:"-"`
}

func CreateTrader(traderType BehaviorType, account float64, wallet string, coinTypeCount uint) *Trader {
	privateKey, err := tools.GeneratePrivateKey(KeySize)
	if err != nil {
		return nil
	}

	time.Sleep(time.Until(time.Now().Truncate(time.Second).Add(time.Second)))
	ticker := time.NewTicker(RoundLength * time.Millisecond)

	return &Trader{
		ID:        tools.SHA256Str(wallet + "-" + strconv.Itoa(int(coinTypeCount))),
		Account:   account,
		Wallet:    wallet,
		PublicKey: &privateKey.PublicKey,
		Data: &TraderData{
			Ticker:        ticker,
			TraderType:    traderType,
			PrivateKey:    privateKey,
			CoinTypeCount: coinTypeCount,
			Traders:       make(map[string]Trader),
			Coins:         make(map[string]CoinTable),
			Cooperations:  make(map[string]CooperationTable),
			BanUntil:      0,
		},
	}
}

func (t *Trader) SaveTrader(trader Trader) error {
	trader.Data = nil
	if _, ok := t.Data.Traders[trader.ID]; ok {
		return errors.New("trader already exist")
	} else if trader.ID != tools.SHA256Str(trader.Wallet+"-"+strconv.Itoa(int(t.Data.CoinTypeCount))) {
		return errors.New("invalid trader ID")
	}

	t.Data.Traders[trader.ID] = trader
	return nil
}

func (t *Trader) CheckForRings(fractalCounter int) *FractalRing {
	if cooperation := t.checkForCooperationRing(); cooperation != nil {
		t.Data.Cooperations[cooperation.ID] = *cooperation
		if t.Data.BanUntil <= fractalCounter {
			return t.checkForFractalRing()
		}
	}
	return nil
}

func (t *Trader) InformFractalRing(fractal FractalRing) error {
	for _, cooperation := range fractal.CooperationRings {
		for _, coinID := range cooperation.CoinIDs {
			if coin, ok := t.Data.Coins[coinID]; !ok {
				return errors.New("coin not found")
			} else if coin.Status != Run {
				return errors.New("coin is not running")
			} else if coin.CooperationID != "" && coin.CooperationID != cooperation.ID {
				if ring, ok := t.Data.Cooperations[coin.CooperationID]; !ok {
					return errors.New("cooperating not found")
				} else if ring.FractalID != "" {
					t.RemoveFractalRing(ring.FractalID)
				} else {
					t.removeCooperatinRing(ring.ID)
				}
			}
		}
	}

	t.saveFractalRing(fractal)
	return nil
}

func (t *Trader) saveFractalRing(fractal FractalRing) {
	for _, cooperation := range fractal.CooperationRings {
		selectedCoins := cooperation.CoinIDs
		t.Data.Cooperations[cooperation.ID] = cooperation
		for i, coinID := range selectedCoins {
			coin := t.Data.Coins[coinID]
			coin.Status = Blocked
			coin.CooperationID = cooperation.ID
			coin.Next = selectedCoins[(i+1)%len(selectedCoins)]
			coin.Prev = selectedCoins[(i-1+len(selectedCoins))%len(selectedCoins)]
			t.Data.Coins[coinID] = coin
		}
	}
}

func (t *Trader) RemoveFractalRing(fractalID string) {
	for _, cooperation := range t.Data.Cooperations {
		if cooperation.FractalID == fractalID {
			t.removeCooperatinRing(cooperation.ID)
		}
	}
}

func (t *Trader) removeCooperatinRing(cooperationID string) {
	for _, coinID := range t.Data.Cooperations[cooperationID].CoinIDs {
		coin := t.Data.Coins[coinID]
		coin.Prev = ""
		coin.Next = ""
		coin.Status = Run
		coin.CooperationID = ""
		t.Data.Coins[coinID] = coin
	}
	delete(t.Data.Cooperations, cooperationID)
}

func (t *Trader) UpdateBalance(traderID string, amount float64) error {
	if trader, ok := t.Data.Traders[traderID]; !ok {
		return errors.New("trader not found")
	} else if trader.Account+amount < 0 {
		return errors.New("insufficient account")
	} else {
		trader.Account += amount
		t.Data.Traders[traderID] = trader
	}
	return nil
}
