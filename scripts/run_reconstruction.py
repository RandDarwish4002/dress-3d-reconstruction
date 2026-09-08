
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT))

from src.reconstruction import TripoSRReconstructor


IMAGE = PROJECT / "input" / "44r3rr.jpg"
OUTPUT = PROJECT / "output" / "reconstruction"


def main():

    reconstructor = TripoSRReconstructor(
        python_path="/content/triposr_env/bin/python",
        triposr_path="/content/dress-3d-reconstruction/triposr",
    )

    reconstructor.reconstruct(
        image_path=IMAGE,
        output_dir=OUTPUT,
        resolution=192,
        chunk_size=4096,
        device="cuda:0",
    )

    print("\n✅ Reconstruction finished.")


if __name__ == "__main__":
    main()
