import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "src.inspect_dataset"], check=True)
    subprocess.run([sys.executable, "-m", "src.prepare_fragments"], check=True)
    subprocess.run([sys.executable, "-m", "src.make_annotation_sample"], check=True)
