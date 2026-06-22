import os
from pathlib import Path
from dotenv import load_dotenv

# Replicate exactly what main.py does
env_path = Path(__file__).parent.parent / ".env"
print(f"Script file: {__file__}")
print(f"Parent: {Path(__file__).parent}")
print(f"Parent.parent: {Path(__file__).parent.parent}")
print(f"Calculated env_path: {env_path}")
print(f"Exists: {env_path.exists()}")

loaded = load_dotenv(dotenv_path=env_path)
print(f"Loaded: {loaded}")

key = os.getenv("ENCRYPTION_KEY")
print(f"ENCRYPTION_KEY found: {key is not None}")
if key:
    print(f"ENCRYPTION_KEY length: {len(key)}")
