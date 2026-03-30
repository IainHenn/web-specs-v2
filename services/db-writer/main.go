package main

import (
	"os"

	"github.com/yourusername/metrics-db-writer/internal/consumer"
)

func getenvWithDefault(key, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}

func main() {
	kafkaBroker := getenvWithDefault("KAFKA_BROKER", "localhost:9092")
	reader := consumer.NewKafkaReader([]string{kafkaBroker}, "metrics.raw")
	defer reader.Close()

	consumer.SendKafkaReads(reader)
}
