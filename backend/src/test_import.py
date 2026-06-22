import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Test 1: Check if .env exists in backend directory
env_path = Path(__file__).parent.parent / ".env"
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

# Test 4: Try importing encryption
try:
    from src.utils.encryption import encrypt, decrypt
    print("OK Successfully imported encryption functions")
except Exception as e:
    print(f"FAIL Failed to import encryption: {e}")
