import grpc
from metrics.v1.metrics_pb2 import Metric
from metrics.v1.metrics_pb2_grpc import MetricsServiceStub
import time


class GRPCClient():
    def __init__(self, server_addr):
        self.server_addr = server_addr
        self.channel = grpc.insecure_channel(self.server_addr)
        self.stub = MetricsServiceStub(self.channel)

    def metrics_dict_to_proto(self, metrics_dict, agent_id="agent-1"):
        metrics_list = []
        timestamp = int(time.time() * 1000)  # ms since epoch

        def _flatten(category, obj, parent_key=None):
            entries = []
            # leaf that carries unit info
            if isinstance(obj, dict) and 'value' in obj and 'unit' in obj and isinstance(obj['value'], (int, float)):
                key = parent_key if parent_key else ''
                entries.append((category, key, float(obj['value']), str(obj['unit'])))
                return entries

            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, dict) and 'value' in v and 'unit' in v and isinstance(v['value'], (int, float)):
                        entries.append((category, new_key, float(v['value']), str(v['unit'])))
                    else:
                        entries.extend(_flatten(category, v, new_key))
                return entries

            if isinstance(obj, list):
                for idx, item in enumerate(obj):
                    new_key = f"{parent_key}.{idx}" if parent_key else str(idx)
                    entries.extend(_flatten(category, item, new_key))
                return entries

            return entries

        for category, values in metrics_dict.items():
            if isinstance(values, dict) or isinstance(values, list):
                entries = _flatten(category, values, None)
                for cat, key, val, unit in entries:
                    metrics_list.append(Metric(
                        agent_id=agent_id,
                        metric_name=cat,
                        value=float(val),
                        unit=unit,
                        timestamp=timestamp,
                        key=key
                    ))
            else:
                # top-level single value with unit
                if isinstance(values, dict) and 'value' in values and 'unit' in values:
                    metrics_list.append(Metric(
                        agent_id=agent_id,
                        metric_name=category,
                        value=float(values['value']),
                        unit=str(values['unit']),
                        timestamp=timestamp,
                        key=''
                    ))
                elif isinstance(values, (int, float)):
                    metrics_list.append(Metric(
                        agent_id=agent_id,
                        metric_name=category,
                        value=float(values),
                        unit='',
                        timestamp=timestamp,
                        key=''
                    ))

        return metrics_list
    
    def send(self, batch):
        ack = self.stub.StreamMetrics(iter(batch))
        return ack.success

    def close(self):
        self.channel.close()