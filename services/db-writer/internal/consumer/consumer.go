package consumer

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	_ "github.com/lib/pq"
	"github.com/segmentio/kafka-go"
	metricsv1 "github.com/yourusername/metrics-ingestion/proto/gen/go/proto/metrics/v1"
	"google.golang.org/protobuf/proto"
)

const batchSize = 250
const flushInterval = 2 * time.Second

func getDBConn() (*sql.DB, error) {
	dbName := getenvWithDefault("DATABASE")
	host := getenvWithDefault("HOST")
	port := getenvWithDefault("PORT")
	user := getenvWithDefault("USER")
	password := getenvWithDefault("PASSWORD")

	connStr := fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable", user, password, host, port, dbName)
	fmt.Println("connStr: ", connStr)
	conn, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}

	if err := conn.Ping(); err != nil {
		_ = conn.Close()
		return nil, err
	}

	return conn, nil
}

func getenvWithDefault(key string) string {
	value := os.Getenv(key)
	return value
}

func NewKafkaReader(brokers []string, topic string) *kafka.Reader {
	groupID := getenvWithDefault("KAFKA_GROUP_ID")
	if groupID == "" {
		groupID = "db-writer"
	}

	return kafka.NewReader(kafka.ReaderConfig{
		Brokers:        brokers,
		Topic:          topic,
		GroupID:        groupID,
		MinBytes:       1,
		MaxBytes:       10e6,
		CommitInterval: 0,
	})
}

func writeMessage(ctx context.Context, conn *sql.DB, metrics []*metricsv1.Metric) error {
	if len(metrics) == 0 {
		return nil
	}

	args := make([]interface{}, 0, len(metrics)*4)
	placeholders := make([]string, 0, len(metrics))

	for i, m := range metrics {
		base := i * 4
		placeholders = append(placeholders,
			fmt.Sprintf("($%d, $%d, $%d, $%d)", base+1, base+2, base+3, base+4),
		)

		timestamp := time.Unix(int64(m.Timestamp), 0).In(time.UTC)

		args = append(args, m.AgentId, m.MetricName, m.Value, timestamp)
	}

	query := `INSERT INTO metrics (agent_id, metric_name, value, timestamp) VALUES ` + strings.Join(placeholders, ", ")
	_, err := conn.ExecContext(ctx, query, args...)
	return err
}

func SendKafkaReads(kafkaReader *kafka.Reader) {
	db, err := getDBConn()
	if err != nil {
		log.Fatal("database connection error: ", err)
	}
	defer db.Close()

	ctx := context.Background()
	msgBatch := make([]kafka.Message, 0, batchSize)
	metricBatch := make([]*metricsv1.Metric, 0, batchSize)

	flushBatch := func() error {
		if len(metricBatch) == 0 {
			return nil
		}

		if err := writeMessage(ctx, db, metricBatch); err != nil {
			return err
		}

		if err := kafkaReader.CommitMessages(ctx, msgBatch...); err != nil {
			return err
		}

		log.Printf("committed batch: metrics=%d", len(metricBatch))
		msgBatch = msgBatch[:0]
		metricBatch = metricBatch[:0]
		return nil
	}

	for {
		readCtx, cancel := context.WithTimeout(ctx, flushInterval)
		message, err := kafkaReader.FetchMessage(readCtx)
		cancel()
		if err != nil {
			if errors.Is(err, context.DeadlineExceeded) {
				if flushErr := flushBatch(); flushErr != nil {
					log.Printf("write/commit error on timed flush: %v", flushErr)
				}
				continue
			}
			log.Printf("read error: %v", err)
			continue
		}

		metric := &metricsv1.Metric{}
		if err := proto.Unmarshal(message.Value, metric); err != nil {
			log.Printf("bad message at offset %d, skipping", message.Offset)
			if commitErr := kafkaReader.CommitMessages(ctx, message); commitErr != nil {
				log.Printf("failed to commit poison message offset %d: %v", message.Offset, commitErr)
			}
			continue
		}

		msgBatch = append(msgBatch, message)
		metricBatch = append(metricBatch, metric)

		if len(metricBatch) < batchSize {
			continue
		}

		if err := flushBatch(); err != nil {
			log.Printf("write/commit error: %v", err)
			continue
		}
	}
}
