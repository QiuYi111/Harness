"""Unit tests for semantic_atlas module and CLI subcommand."""

import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from scripts.harness_runtime.semantic_atlas import (
    EXTENSION_LANGUAGE_MAP,
    assemble_prompt,
    detect_language,
    load_skill_prompt,
    load_template,
    resolve_output_path,
)
from scripts.harness_runtime.cli import main

_PID_FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "subskills"
    / "atlas"
    / "examples"
    / "pid_controller.h"
)


class TestDetectLanguage(unittest.TestCase):

    def test_all_supported_extensions(self):
        for ext, expected_lang in EXTENSION_LANGUAGE_MAP.items():
            with self.subTest(ext=ext):
                path = Path(f"foo{ext}")
                self.assertEqual(detect_language(path), expected_lang)

    def test_unsupported_extension_raises(self):
        with self.assertRaises(ValueError):
            detect_language("readme.md")

    def test_case_insensitive(self):
        self.assertEqual(detect_language("main.PY"), "python")
        self.assertEqual(detect_language("code.CPP"), "cpp")


class TestResolveOutputPath(unittest.TestCase):

    def test_default_output_dir(self):
        result = resolve_output_path("src/main.py")
        expected = Path("docs") / "semantic_atlas" / "main.semantic_atlas.md"
        self.assertEqual(result, expected)

    def test_custom_output_dir(self):
        result = resolve_output_path("src/main.py", output_dir="/tmp/atlas")
        expected = Path("/tmp/atlas") / "main.semantic_atlas.md"
        self.assertEqual(result, expected)

    def test_custom_output_dir_preserves_stem(self):
        result = resolve_output_path("lib/utils.rs", output_dir="out")
        self.assertEqual(result, Path("out") / "utils.semantic_atlas.md")


class TestLoadTemplate(unittest.TestCase):

    def test_returns_non_empty_string(self):
        template = load_template()
        self.assertIsInstance(template, str)
        self.assertTrue(len(template) > 0)

    def test_missing_template_raises(self):
        with patch(
            "scripts.harness_runtime.semantic_atlas.ATLAS_SUBSKILL_DIR",
            Path("/nonexistent/path/that/does/not/exist"),
        ):
            with self.assertRaises(FileNotFoundError):
                load_template()


class TestLoadSkillPrompt(unittest.TestCase):

    def test_returns_non_empty_string(self):
        prompt = load_skill_prompt()
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)

    def test_missing_skill_raises(self):
        with patch(
            "scripts.harness_runtime.semantic_atlas.ATLAS_SUBSKILL_DIR",
            Path("/nonexistent/path/that/does/not/exist"),
        ):
            with self.assertRaises(FileNotFoundError):
                load_skill_prompt()


class TestAssemblePrompt(unittest.TestCase):

    def setUp(self):
        self.template = load_template()
        self.source = "int main() { return 0; }"

    def test_contains_source_code(self):
        prompt = assemble_prompt(self.source, "cpp", self.template)
        self.assertIn("int main() { return 0; }", prompt)

    def test_contains_language(self):
        prompt = assemble_prompt(self.source, "cpp", self.template)
        self.assertIn("Language: cpp", prompt)

    def test_contains_template(self):
        prompt = assemble_prompt(self.source, "cpp", self.template)
        self.assertIn("Output Template", prompt)

    def test_no_flags_by_default(self):
        prompt = assemble_prompt(self.source, "cpp", self.template)
        self.assertNotIn("Active Flags", prompt)

    def test_strict_flag(self):
        prompt = assemble_prompt(self.source, "cpp", self.template, strict=True)
        self.assertIn("Active Flags", prompt)
        self.assertIn("STRICT MODE", prompt)

    def test_diagram_heavy_flag(self):
        prompt = assemble_prompt(
            self.source, "cpp", self.template, diagram_heavy=True
        )
        self.assertIn("Active Flags", prompt)
        self.assertIn("DIAGRAM-HEAVY MODE", prompt)

    def test_verify_mermaid_flag(self):
        prompt = assemble_prompt(
            self.source, "cpp", self.template, verify_mermaid=True
        )
        self.assertIn("Active Flags", prompt)
        self.assertIn("MERMAID VERIFICATION", prompt)

    def test_all_flags(self):
        prompt = assemble_prompt(
            self.source,
            "cpp",
            self.template,
            strict=True,
            diagram_heavy=True,
            verify_mermaid=True,
        )
        self.assertIn("STRICT MODE", prompt)
        self.assertIn("DIAGRAM-HEAVY MODE", prompt)
        self.assertIn("MERMAID VERIFICATION", prompt)


class TestAtlasCli(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_success_with_fixture(self):
        self.assertTrue(
            _PID_FIXTURE.exists(),
            f"Fixture missing: {_PID_FIXTURE}",
        )
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["atlas", str(_PID_FIXTURE)])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Generating semantic atlas", result.output)
            self.assertIn("Prompt written to:", result.output)
            out_path = Path("docs") / "semantic_atlas" / "pid_controller.semantic_atlas.md"
            self.assertTrue(out_path.exists())
            content = out_path.read_text(encoding="utf-8")
            self.assertIn("pid_controller", content)

    def test_error_missing_file(self):
        result = self.runner.invoke(main, ["atlas", "/nonexistent/file.py"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("not found", result.output)

    def test_error_directory_input(self):
        with self.runner.isolated_filesystem():
            dir_path = Path("some_dir")
            dir_path.mkdir()
            result = self.runner.invoke(main, ["atlas", str(dir_path)])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("directory input not supported", result.output)

    def test_custom_output_dir(self):
        self.assertTrue(_PID_FIXTURE.exists())
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                main, ["atlas", str(_PID_FIXTURE), "--output-dir", "my_output"]
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            out_path = Path("my_output") / "pid_controller.semantic_atlas.md"
            self.assertTrue(out_path.exists())

    def test_strict_flag(self):
        self.assertTrue(_PID_FIXTURE.exists())
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                main, ["atlas", str(_PID_FIXTURE), "--strict"]
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Strict:    True", result.output)

    def test_language_override(self):
        self.assertTrue(_PID_FIXTURE.exists())
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                main, ["atlas", str(_PID_FIXTURE), "--language", "cpp"]
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Language:  cpp", result.output)


if __name__ == "__main__":
    unittest.main()
