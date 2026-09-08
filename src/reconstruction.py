
from pathlib import Path
import subprocess


class TripoSRReconstructor:
    """
    Main interface for converting a single image into a 3D mesh.
    """

    def __init__(
        self,
        python_path="/content/triposr_env/bin/python",
        triposr_path="/content/dress-3d-reconstruction/triposr",
    ):
        self.python_path = python_path
        self.triposr_path = Path(triposr_path)

        self.run_script = self.triposr_path / "run.py"

        if not Path(self.python_path).exists():
            raise FileNotFoundError(
                f"Python environment not found: {self.python_path}"
            )

        if not self.run_script.exists():
            raise FileNotFoundError(
                f"TripoSR run.py not found: {self.run_script}"
            )

    def reconstruct(
        self,
        image_path,
        output_dir,
        resolution=192,
        chunk_size=4096,
        device="cuda:0",
    ):
        """
        Run TripoSR reconstruction.

        Parameters
        ----------
        image_path : str
            Input image.
        output_dir : str
            Output directory.
        resolution : int
            Marching Cubes resolution.
        chunk_size : int
            Renderer chunk size.
        device : str
            CUDA device.
        """

        image_path = Path(image_path)
        output_dir = Path(output_dir)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Input image not found: {image_path}"
            )

        output_dir.mkdir(parents=True, exist_ok=True)

        command = [
            self.python_path,
            str(self.run_script),
            str(image_path),
            "--device",
            device,
            "--output-dir",
            str(output_dir),
            "--model-save-format",
            "obj",
            "--chunk-size",
            str(chunk_size),
            "--mc-resolution",
            str(resolution),
        ]

        print("🚀 Running TripoSR...")
        print(" ".join(command))

        result = subprocess.run(
            command,
            check=True,
            text=True,
        )

        return output_dir
