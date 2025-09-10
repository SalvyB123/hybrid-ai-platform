import textwrap
from pathlib import Path

from src.ai.faq.data_loader import load_faqs


def test_load_faqs_parses_yaml(tmp_path: Path):
    p = tmp_path / "faqs.yaml"
    p.write_text(
        textwrap.dedent(
            """
        - id: x
          question: "Q?"
          answer: "A."
    """
        ).strip()
    )
    faqs = load_faqs(p)
    assert len(faqs) == 1
    assert faqs[0].id == "x"
    assert faqs[0].answer == "A."
