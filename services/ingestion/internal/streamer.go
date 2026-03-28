package internal

import (
	"io"
	"log"

	"github.com/segmentio/kafka-go"
	metricsv1 "github.com/yourusername/metrics-ingestion/proto/gen/go/proto/metrics/v1"
)

type Server struct {
	metricsv1.UnimplementedMetricsServiceServer
	Writer *kafka.Writer
}

func (s *Server) StreamMetrics(stream metricsv1.MetricsService_StreamMetricsServer) error {
	var buffer []*metricsv1.Metric
	for {
		metric, err := stream.Recv()
		if err == io.EOF {
			break
		}

		if err != nil {
			log.Printf("stream receive error: %v", err)
			return err
		}

		buffer = append(buffer, metric)
	}

	if len(buffer) >= 500 {
		if err := sendToKafka(buffer, s.Writer); err != nil {
			log.Printf("kafka send error: %v", err)
			return err
		}
		buffer = buffer[:0]
	}

	return stream.SendAndClose(&metricsv1.Ack{Success: true})
}
