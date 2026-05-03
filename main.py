import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*SymbolDatabase.GetPrototype\(\) is deprecated.*")

# Lightweight .env loader (no extra dependency required)
env_path = Path('.env')
if env_path.exists():
    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in __import__('os').environ:
            __import__('os').environ[k] = v

from studybuddy.ui import run

if __name__ == "__main__":
    run()
