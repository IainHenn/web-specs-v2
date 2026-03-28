package main

import (
	"log"
	"net"

	"github.com/yourusername/metrics-ingestion/internal"
	metricsv1 "github.com/yourusername/metrics-ingestion/proto/gen/go/proto/metrics/v1"
	"google.golang.org/grpc"
)

func main() {
	writer := internal.NewKafkaWriter([]string{"localhost:9092"}, "metrics.raw")
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
