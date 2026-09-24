"""Audit entry point: regenerates the paper figures via cvr.figures (repo root as cwd)."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from cvr.figures import main  # noqa: E402

main()
