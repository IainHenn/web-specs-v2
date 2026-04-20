FROM golang:latest AS builder

WORKDIR /src

# Copy module files first for better layer caching.
COPY services/ingestion/go.mod services/ingestion/go.sum ./services/ingestion/
COPY services/db-writer/go.mod services/db-writer/go.sum ./services/db-writer/

WORKDIR /src/services/db-writer
RUN go mod download

WORKDIR /src
COPY services/ingestion ./services/ingestion
COPY services/db-writer ./services/db-writer

WORKDIR /src/services/db-writer
RUN CGO_ENABLED=0 GOOS=linux go build -o /out/db-writer ./main.go

FROM gcr.io/distroless/base-debian12

WORKDIR /app
COPY --from=builder /out/db-writer /app/db-writer

ENTRYPOINT ["/app/db-writer"]
