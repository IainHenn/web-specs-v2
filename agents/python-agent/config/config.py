import json
import io
import os
from pathlib import Path


def get_agent_id():
	env_path = Path(__file__).resolve().parents[3] / ".env"
	agent_id = ""

	if env_path.exists():
		for line in env_path.read_text(encoding="utf-8").splitlines():
			line = line.strip()
			if not line or line.startswith("#"):
				continue
			if line.startswith("AGENT_ID="):
				agent_id = line.split("=", 1)[1].strip().strip('"').strip("'")
				break

	if not agent_id:
		agent_id = os.getenv("AGENT_ID", "")

	return agent_id

def get_server_address():
	env_path = Path(__file__).resolve().parents[3] / ".env"
	server_address = ""

	if env_path.exists():
		for line in env_path.read_text(encoding="utf-8").splitlines():
			line = line.strip()
			if not line or line.startswith("#"):
				continue
			if line.startswith("SERVER_ADDRESS="):
				server_address = line.split("=", 1)[1].strip().strip('"').strip("'")
				break

	if not server_address:
		server_address = os.getenv("SERVER_ADDRESS", "")

	return server_address