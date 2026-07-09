import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from src.config import MODELS_DIR, RANDOM_STATE
from src.labels import resolve_labeled_fragments

MODEL_NAME = "cointegrated/rubert-tiny2"


def main():
    try:
        from datasets import Dataset
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
    except ImportError as e:
        raise SystemExit("Установите torch transformers datasets accelerate") from e

    df, label_path, label_source = resolve_labeled_fragments(allow_weak_fallback=False)
    df = df[df["label"].isin(["optimism", "skepticism", "mixed"])].copy()
    print(f"RuBERT использует файл разметки: {label_path} ({label_source}), строк: {len(df)}")

    label2id = {"optimism": 0, "skepticism": 1, "mixed": 2}
    id2label = {v: k for k, v in label2id.items()}
    df["labels"] = df["label"].map(label2id)

    train_df, test_df = train_test_split(
        df[["fragment_text", "labels"]],
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=df["labels"]
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tok(batch):
        return tokenizer(batch["fragment_text"], truncation=True, padding="max_length", max_length=192)

    train_ds = Dataset.from_pandas(train_df.reset_index(drop=True)).map(tok, batched=True)
    test_ds = Dataset.from_pandas(test_df.reset_index(drop=True)).map(tok, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=3, id2label=id2label, label2id=label2id
    )

    args = TrainingArguments(
        output_dir=str(MODELS_DIR / "rubert_tiny2"),
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=4,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        seed=RANDOM_STATE
    )

    trainer = Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=test_ds, tokenizer=tokenizer)
    trainer.train()
    pred = trainer.predict(test_ds)
    y_pred = np.argmax(pred.predictions, axis=1)
    print(classification_report(test_df["labels"], y_pred, target_names=[id2label[i] for i in range(3)], digits=4))
    trainer.save_model(str(MODELS_DIR / "rubert_tiny2_final"))
    tokenizer.save_pretrained(str(MODELS_DIR / "rubert_tiny2_final"))


if __name__ == "__main__":
    main()
