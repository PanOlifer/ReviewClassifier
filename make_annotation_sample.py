import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "src.00_inspect_dataset"], check=True)
    subprocess.run([sys.executable, "-m", "src.01_prepare_fragments"], check=True)
    subprocess.run([sys.executable, "-m", "src.02_make_annotation_sample"], check=True)
