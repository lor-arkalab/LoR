package main

import (
	"flag"
	"log"
	"time"

	"github.com/Arka-Lab/LoR/internal"
	"github.com/Arka-Lab/LoR/pkg"
)

func ParseFlags() (int, time.Duration, int, int, int, string, string) {
	typesPtr := flag.Int("type", 3, "number of coin types")
	runTimePtr := flag.Int("time", 60, "run time in seconds")
	tradersPtr := flag.Int("trader", 100, "number of traders")
	randomsPtr := flag.Int("random", 0, "number of random traders")
	badsPtr := flag.Int("bad", 0, "number of bad traders")
	alphaPtr := flag.Float64("alpha", pkg.BadBehavior, "bad behavior percentage")
	saveTohPtr := flag.String("save-to", "system.json", "file path to save system")
	loadFromhPtr := flag.String("load-from", "", "file path to load system")
	flag.Parse()

	if *typesPtr < 1 {
		log.Fatalf("Number of types must be positive\n")
	} else if *tradersPtr < 1 {
		log.Fatalf("Number of traders must be positive\n")
	}
	numTypes, numTraders := *typesPtr, *tradersPtr

	if *runTimePtr < 0 {
		log.Fatalf("Run time must be non-negative\n")
	}
	runTime := time.Duration(*runTimePtr) * time.Second

	if *randomsPtr < 0 || *badsPtr < 0 {
		log.Fatalf("Number of random and bad traders must be non-negative\n")
	} else if *randomsPtr+*badsPtr > numTraders {
		log.Fatalf("Number of random and bad traders must be less than the total number of traders\n")
	}
	numRandoms, numBads := *randomsPtr, *badsPtr

	saveTo, loadFrom := *saveTohPtr, *loadFromhPtr

	if *alphaPtr < 0 || *alphaPtr > 1 {
		log.Fatalf("Bad behavior percentage must be between 0 and 1\n")
	}
	pkg.BadBehavior = *alphaPtr

	return numTypes, runTime, numTraders, numRandoms, numBads, saveTo, loadFrom
}

func main() {
	logger := log.Default()
	var system *internal.System
	numTypes, runTime, numTraders, numRandoms, numBads, saveTo, loadFrom := ParseFlags()

	if loadFrom == "" {
		finish := make(chan bool, 1)
		system = internal.NewSystem()

		logger.Printf("Starting simulation with %d types (alpha = %.2f%%)...\n", numTypes, pkg.BadBehavior*100)
		if err := system.Init(numTraders, numRandoms, numBads, uint(numTypes)); err != nil {
			logger.Fatalf("Error initializing system: %v\n", err)
		}
		logger.Println("Simulation initialized!")

		logger.Println("Starting simulation...")
		done := make(chan bool, 1)
		go func() {
			system.Start(finish)
			done <- true
		}()
		logger.Println("Simulation started!")

		logger.Printf("Waiting for %s...\n", runTime)
		time.Sleep(runTime)
		finish <- true
		<-done
		logger.Println("Simulation stopped!")

		if err := system.Save(saveTo); err != nil {
			logger.Fatalf("Error saving system: %v\n", err)
		}
		logger.Printf("System saved to %s\n", saveTo)
	} else {
		s, err := internal.Load(loadFrom)
		if err != nil {
			logger.Fatalf("Error loading system: %v\n", err)
		}

		system = s
		logger.Printf("Simulation loaded from %s\n", loadFrom)
	}

	internal.AnalyzeSystem(system)
}
