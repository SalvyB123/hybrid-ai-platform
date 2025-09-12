import csv

from src.ai.sentiment.rule_based import classify

DEVSET = "data/sentiment/devset.csv"


def test_rule_based_on_devset():
    rows = list(csv.DictReader(open(DEVSET)))
    correct = 0
    for r in rows:
        res = classify(r["text"])
        correct += int(res.label == r["gold_label"])
    # With the dampening + windowed negation, expect >=9 correct
    assert correct >= 9, f"Expected >=9 correct, got {correct}"
