"""Allow running the mukip CLI via `python -m mukip`."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
