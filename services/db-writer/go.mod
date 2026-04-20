module github.com/yourusername/metrics-db-writer

go 1.26.1

require (
	github.com/lib/pq v1.10.9
	github.com/segmentio/kafka-go v0.4.50
	github.com/yourusername/metrics-ingestion v0.0.0
	google.golang.org/protobuf v1.33.0
)

require (
	github.com/klauspost/compress v1.17.9 // indirect
	github.com/pierrec/lz4/v4 v4.1.15 // indirect
	golang.org/x/net v0.38.0 // indirect
	golang.org/x/sys v0.31.0 // indirect
	golang.org/x/text v0.23.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20240318140521-94a12d6c2237 // indirect
	google.golang.org/grpc v1.64.1 // indirect
)

replace github.com/yourusername/metrics-ingestion => ../ingestion
