import subprocess
import sys

STEPS = [
    "src.00_inspect_dataset",
    "src.01_prepare_fragments",
    "src.03_build_weak_labels",
    "src.04_train_baseline",
    "src.05_predict_fragments",
    "src.06_aggregate_results",
    "src.07_make_heatmaps",
    "src.08_lexical_analysis",
]

def main():
    for step in STEPS:
        print("\\n" + "=" * 90)
        print(f"RUN {step}")
        print("=" * 90)
        subprocess.run([sys.executable, "-m", step], check=True)

if __name__ == "__main__":
    main()
