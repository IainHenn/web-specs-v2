import grpc
from proto.gen.python.metrics.v1.metrics_pb2 import Metric, Ack
from proto.gen.python.metrics.v1.metrics_pb2_grpc import MetricsServiceStub
import time

class GRPCClient():
    def __init__(self, server_addr):
        self.server_addr = server_addr
        self.channel = None # gRPC connection to server
        self.stub = None # object to call RPC methods on
        self.stream = None # streaming object (where we send the metrics to)

    
    def connect(self):
        self.channel = grpc.insecure_channel(self.server_addr)
        self.stub = MetricsServiceStub
        self.stream = self.stub.StreamMetrics()


    def metrics_dict_to_proto(metrics_dict, agent_id="agent-1"):
        metrics_list = []
        timestamp = int(time.time() * 1000)  # ms since epoch
        for category, values in metrics_dict.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    # flatten nested dicts if necessary
                    if isinstance(value, dict):
                        for sub_key, sub_val in value.items():
                            metrics_list.append(Metric(
                                agent_id=agent_id,
                                metric_name=f"{category}.{key}.{sub_key}",
                                value=float(sub_val),
                                timestamp=timestamp
                            ))
                    else:
                        metrics_list.append(Metric(
                            agent_id=agent_id,
                            metric_name=f"{category}.{key}",
                            value=float(value),
                            timestamp=timestamp
                        ))
        return metrics_list
    
    def send(self, batch):
        for metric in batch:
            self.stream.write(metric)

        ack = self.stream.read()

        return ack.success

    def close(self):
        self.stream.close()
        self.channel.close()