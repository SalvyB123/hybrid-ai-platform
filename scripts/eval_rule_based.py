import csv
import pathlib
import sys
import time

# Make imports work whether run as `python -m scripts.eval_rule_based` or directly
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from src.ai.sentiment.rule_based import classify  # noqa: E402


def main():
    rows = list(csv.DictReader(open("data/sentiment/devset.csv")))
    start = time.perf_counter()
    correct = 0
    neutral_count = 0
    mistakes = []
    for r in rows:
        res = classify(r["text"])
        ok = res.label == r["gold_label"]
        correct += int(ok)
        neutral_count += int(res.label == "neutral")
        if not ok:
            mistakes.append((r["id"], r["gold_label"], res.label, r["text"]))
    dur_ms = (time.perf_counter() - start) * 1000.0
    print(f"Samples: {len(rows)}")
    print(f"Accuracy: {correct}/{len(rows)} = {correct/len(rows):.2f}")
    print(f"Neutral rate: {neutral_count/len(rows):.2f}")
    print(f"Avg latency (ms/sample): {dur_ms/len(rows):.2f}")
    if mistakes:
        print("\nMisclassifications:")
        for mid, gold, pred, txt in mistakes:
            print(f"- id={mid} gold={gold} pred={pred} :: {txt}")


if __name__ == "__main__":
    main()
