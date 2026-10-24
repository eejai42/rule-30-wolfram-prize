"""Build the rulebook: clear the caches, effortless build, fill the caches, build again, refresh the editor.

Use this instead of a bare `effortless build` (which would compile with whatever caches the file holds).
Usage: python3 research/build.py
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_tools as lt

print(json.dumps(lt.build(), indent=1))
