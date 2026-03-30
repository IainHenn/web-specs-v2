from collector.system_metrics import async_collect_metrics
from config.config import get_agent_id
import asyncio

async def stream_loop(grpc_client, batch_size=500, interval=1):
    buffer = []

    while True:
        metrics = await async_collect_metrics()
        agent_id = get_agent_id()

        metrics = grpc_client.metrics_dict_to_proto(metrics, agent_id)

        buffer.extend(metrics)

        # Only send data when we're over the batch size
        if len(buffer) >= batch_size:
            batch = buffer[:batch_size]
            await asyncio.get_running_loop().run_in_executor(None, grpc_client.send, batch)
            del buffer[:batch_size]

        # Keep some flow even if batch size is not reached yet.
        if buffer and len(buffer) < batch_size:
            await asyncio.get_running_loop().run_in_executor(None, grpc_client.send, list(buffer))
            buffer.clear()

        await asyncio.sleep(interval)
