"""Tests for scripts.harness_runtime.mermaid_verify."""

import unittest

from scripts.harness_runtime.mermaid_verify import verify_mermaid_syntax


class TestVerifyMermaidSyntax(unittest.TestCase):
    """Tests for verify_mermaid_syntax()."""

    def test_valid_flowchart(self):
        text = """\
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[OK]
    B -->|No| D[Fail]
"""
        valid, msg = verify_mermaid_syntax(text)
        self.assertTrue(valid, msg)
        self.assertEqual(msg, "")

    def test_valid_state_diagram_v2(self):
        text = """\
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : Start
    Processing --> Done : Finish
    Done --> [*]
"""
        valid, msg = verify_mermaid_syntax(text)
        self.assertTrue(valid, msg)
        self.assertEqual(msg, "")

    def test_unmatched_square_brackets(self):
        text = "flowchart TD\n    A[Start --> B[End]\n"
        valid, msg = verify_mermaid_syntax(text)
        self.assertFalse(valid)
        self.assertIn("Unbalanced square brackets", msg)

    def test_unmatched_curly_braces(self):
        text = "flowchart TD\n    A{Decision\n"
        valid, msg = verify_mermaid_syntax(text)
        self.assertFalse(valid)
        self.assertIn("Unbalanced curly braces", msg)

    def test_empty_string(self):
        valid, msg = verify_mermaid_syntax("")
        self.assertFalse(valid)
        self.assertEqual(msg, "Empty diagram")

    def test_whitespace_only(self):
        valid, msg = verify_mermaid_syntax("   \n  \t  ")
        self.assertFalse(valid)
        self.assertEqual(msg, "Empty diagram")

    def test_plain_text_no_mermaid(self):
        text = "This is just some random text with no diagram"
        valid, msg = verify_mermaid_syntax(text)
        self.assertFalse(valid)
        self.assertIn("Invalid diagram type", msg)

    def test_invalid_diagram_type(self):
        text = "bogusDiagram TD\n    A --> B\n"
        valid, msg = verify_mermaid_syntax(text)
        self.assertFalse(valid)
        self.assertIn("Invalid diagram type", msg)

    def test_valid_sequence_diagram(self):
        text = """\
sequenceDiagram
    Alice->>Bob: Hello
    Bob-->>Alice: Hi
"""
        valid, msg = verify_mermaid_syntax(text)
        self.assertTrue(valid, msg)
        self.assertEqual(msg, "")

    def test_valid_graph_keyword(self):
        text = "graph LR\n    A --> B\n"
        valid, msg = verify_mermaid_syntax(text)
        self.assertTrue(valid, msg)
        self.assertEqual(msg, "")

    def test_multiple_diagrams_validated_separately(self):
        """Each diagram must be validated individually — one bad invalidates."""
        good = "flowchart TD\n    A --> B\n"
        bad = "flowchart TD\n    A[Start --> B[End]\n"
        valid, msg = verify_mermaid_syntax(good)
        self.assertTrue(valid, msg)
        valid, msg = verify_mermaid_syntax(bad)
        self.assertFalse(valid)

    def test_flowchart_with_subgraph(self):
        text = """\
flowchart TD
    subgraph Cluster
        A[Start] --> B[End]
    end
"""
        valid, msg = verify_mermaid_syntax(text)
        self.assertTrue(valid, msg)
        self.assertEqual(msg, "")


if __name__ == "__main__":
    unittest.main()
