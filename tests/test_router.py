import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.router.data_router import choose_engine

engine = choose_engine("file", 100)
print(f"Chosen engine: {engine}")