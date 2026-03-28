from streamer.stream_loop import stream_loop
from client.grpc_client import GRPCClient
from config.config import get_server_address
def main():
    server_address = get_server_address()
    grpc_client = GRPCClient(server_address)
    stream_loop(grpc_client)