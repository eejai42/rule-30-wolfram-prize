"""Build the rulebook: clear the caches, effortless build, fill the caches, build again, refresh the editor.

Use this instead of a bare `effortless build` (which would compile with whatever caches the file holds).
It refuses to build while an evidence file differs from its recorded sha256.
Usage: python3 research/build.py [--refresh-evidence]   (re-hash changed evidence files first, then build)
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_tools as lt

if '--refresh-evidence' in sys.argv:
    print('evidence re-hashed:', lt.refresh_evidence())
print(json.dumps(lt.build(), indent=1))
