FROM golang:latest AS builder

WORKDIR /src

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o /out/ingestion ./main.go

FROM gcr.io/distroless/base-debian12

WORKDIR /app
COPY --from=builder /out/ingestion /app/ingestion

EXPOSE 50051

ENTRYPOINT ["/app/ingestion"]
