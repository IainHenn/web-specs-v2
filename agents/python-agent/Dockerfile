FROM python:3.12-slim

ARG TARGETOS=linux

WORKDIR /app

COPY agents/python-agent/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Enable Windows disk performance counters only for Windows builds.
RUN if [ "$TARGETOS" = "windows" ]; then \
      diskperf -y; \
    fi

COPY proto /app/proto
COPY agents/python-agent /app/agents/python-agent

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/proto/gen/python

WORKDIR /app/agents/python-agent
CMD ["python", "-c", "from main import main; main()"]
