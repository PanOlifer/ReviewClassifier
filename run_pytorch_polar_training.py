"""Run enhanced PyTorch polar validation."""
import subprocess
import sys

subprocess.run([sys.executable, "-m", "src.train_pytorch_polar_classifier"], check=True)
