"""Run enhanced PyTorch polar validation."""
import subprocess
import sys

subprocess.run([sys.executable, "-m", "src.11_train_pytorch_polar_classifier"], check=True)
