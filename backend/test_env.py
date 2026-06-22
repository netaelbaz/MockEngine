import os
from dotenv import load_dotenv
from pathlib import Path

# Test 1: Check if .env exists in backend directory
env_path = Path(__file__).parent / ".env"
print(f"Script: {__file__}")
print(f"Env path: {env_path}")
print(f"Exists: {env_path.exists()}")

# Test 2: Try to load it
loaded = load_dotenv(dotenv_path=env_path)
print(f"Loaded: {loaded}")

# Test 3: Check environment variable
key = os.getenv("ENCRYPTION_KEY")
print(f"ENCRYPTION_KEY found: {key is not None}")
if key:
    print(f"ENCRYPTION_KEY length: {len(key)}")
