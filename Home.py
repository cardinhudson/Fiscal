"""Alias em minúsculo para rodar via `streamlit run home.py`.

Ele delega para app/Home.py para manter o código original intacto.
"""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    target = Path(__file__).parent / "app" / "Home.py"
    runpy.run_path(str(target), run_name="__main__")
