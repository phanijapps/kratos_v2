from pathlib import Path

NUM_NERD = (Path(__file__).parent / "number_nerd.md").read_text(encoding="utf-8")
THINKER = (Path(__file__).parent / "thinker.md").read_text(encoding="utf-8")
REPORTER = (Path(__file__).parent / "reporter.md").read_text(encoding="utf-8")