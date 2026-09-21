"""Put ops/ and ops/time/ on sys.path so the tested scripts import as modules.

The scripts are CLI tools, not a package; none of them do work at import time
(every one guards its entry point with __name__ == "__main__"), so importing
them here is safe and needs no fixtures on disk.
"""
import os, sys

OPS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (OPS, os.path.join(OPS, "time"), os.path.join(OPS, "bin")):
    if p not in sys.path:
        sys.path.insert(0, p)
