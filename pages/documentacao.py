"""Wrapper de página (Streamlit multipage).

Delegação para app/pages/documentacao.py.
"""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "app" / "pages" / "documentacao.py"
    runpy.run_path(str(target), run_name="__main__")
