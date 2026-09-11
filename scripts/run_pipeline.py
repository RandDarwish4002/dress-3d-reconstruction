#!/usr/bin/env python
"""CLI entry point.

Usage:
    python scripts/run_pipeline.py --front input/front.jpg --back input/back.jpg --name my_dress
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dress3d.config import PipelineConfig  # noqa: E402
from dress3d.pipeline import DressReconstructionPipeline  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reconstruct a single textured 3D garment from front/back photos."
    )
    parser.add_argument("--front", required=True, type=Path, help="Path to the front-view photo")
    parser.add_argument("--back", required=True, type=Path, help="Path to the back-view photo")
    parser.add_argument("--name", default="garment", help="Output subfolder / file name")
    args = parser.parse_args()

    config = PipelineConfig()
    pipeline = DressReconstructionPipeline(config)
    result = pipeline.run(args.front, args.back, args.name)

    print(f"✅ Done. Final textured model: {result}")


if __name__ == "__main__":
    main()
