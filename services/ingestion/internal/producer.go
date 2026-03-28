package internal

import (
	"context"
	"log"

	"github.com/segmentio/kafka-go"
	metricsv1 "github.com/yourusername/metrics-ingestion/proto/gen/go/proto/metrics/v1"
	"google.golang.org/protobuf/proto"
)

// NewKafkaWriter creates a kafka writer for the given broker list and topic.
func NewKafkaWriter(brokers []string, topic string) *kafka.Writer {
	return kafka.NewWriter(kafka.WriterConfig{
		Brokers: brokers,
		Topic:   topic,
	})
}

func sendToKafka(buffer []*metricsv1.Metric, kafkaWriter *kafka.Writer) error {
	var messages []kafka.Message

	for _, metric := range buffer {
		data, err := proto.Marshal(metric)
		if err != nil {
			log.Printf("issue marshaling metric: %v", err)
			continue
		}

		msg := kafka.Message{
			Key:   []byte(metric.AgentId),
			Value: data,
		}
		messages = append(messages, msg)
	}

	err := kafkaWriter.WriteMessages(context.Background(), messages...)
	if err != nil {
		log.Printf("failed to write kafka messages: %v", err)
		return err
	}

	return nil
}
