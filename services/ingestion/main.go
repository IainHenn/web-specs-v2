package main

import (
	"log"
	"net"
	"os"

	"github.com/yourusername/metrics-ingestion/internal"
	metricsv1 "github.com/yourusername/metrics-ingestion/proto/gen/go/proto/metrics/v1"
	"google.golang.org/grpc"
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
	writer := internal.NewKafkaWriter([]string{kafkaBroker}, "metrics.raw")
	defer writer.Close()

	grpcServer := grpc.NewServer()
	metricsv1.RegisterMetricsServiceServer(grpcServer, &internal.Server{Writer: writer})

	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("failed to serve gRPC server: %v", err)
	}
}
