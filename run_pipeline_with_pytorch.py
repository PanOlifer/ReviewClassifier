import subprocess
import sys

STEPS = [
    "src.inspect_dataset",
    "src.prepare_fragments",
    "src.build_weak_labels",
    "src.train_baseline",
    "src.predict_fragments",
    "src.aggregate_results",
    "src.make_heatmaps",
    "src.lexical_analysis",
    "src.train_pytorch_classifier",
]


def main():
    for step in STEPS:
        print("\n" + "=" * 90)
        print(f"RUN {step}")
        print("=" * 90)
        subprocess.run([sys.executable, "-m", step], check=True)


if __name__ == "__main__":
    main()
