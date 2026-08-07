from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from project_doctor.analyzer import analyze_repository
from project_doctor.reporting import validate_output_directory, write_reports


class ProjectDoctorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.repository = self.root / "client-project"
        self.repository.mkdir()
        self.output = self.root / "report-output"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write(self, relative_path: str, content: str) -> Path:
        target = self.repository / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def test_writes_matching_json_and_markdown_without_secret_value(self) -> None:
        self.write("README.md", "# Client project\n")
        self.write("pyproject.toml", "[project]\nname = 'client-project'\n")
        self.write("tests/test_health.py", "def test_ok():\n    assert True\n")
        self.write("src/app.py", 'API_TOKEN = "super-secret-value-123456"\n')
        self.write(".env", "DATABASE_PASSWORD=never-put-this-in-a-report\n")

        result = analyze_repository(self.repository, client="Acme")
        safe_output = validate_output_directory(self.repository, self.output)
        report_paths = write_reports(result, safe_output)

        report_json = json.loads(report_paths["json"].read_text(encoding="utf-8"))
        markdown = report_paths["markdown"].read_text(encoding="utf-8")
        rule_ids = {item["rule_id"] for item in report_json["findings"]}

        self.assertEqual(report_json["audit_id"], result.audit_id)
        self.assertIn("secrets.credential_assignment", rule_ids)
        self.assertIn("secrets.sensitive-file-name", rule_ids)
        self.assertNotIn("super-secret-value-123456", report_paths["json"].read_text(encoding="utf-8"))
        self.assertNotIn("super-secret-value-123456", markdown)
        self.assertNotIn("never-put-this-in-a-report", markdown)
        self.assertNotIn("never-put-this-in-a-report", report_paths["json"].read_text(encoding="utf-8"))
        self.assertNotIn(str(self.repository), markdown)
        self.assertNotIn(str(self.repository), report_paths["json"].read_text(encoding="utf-8"))

    def test_auditing_source_never_executes_it(self) -> None:
        marker = self.root / "must-not-exist.txt"
        self.write(
            "evil.py",
            "from pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('this code must never run')\n",
        )

        analyze_repository(self.repository)

        self.assertFalse(marker.exists())

    def test_rejects_report_output_inside_the_target_repository(self) -> None:
        with self.assertRaises(ValueError):
            validate_output_directory(self.repository, self.repository / "reports")

    def test_reports_syntax_errors_and_bounded_coverage(self) -> None:
        self.write("broken.py", "def incomplete(:\n    pass\n")
        self.write("large.py", "x" * 1024)

        result = analyze_repository(self.repository, max_file_bytes=100)

        rule_ids = {finding.rule_id for finding in result.findings}
        self.assertIn("python.syntax-error", rule_ids)
        self.assertEqual(result.coverage["status"], "partial")
        self.assertGreater(result.coverage["skipped"].get("file_size_limit", 0), 0)

    def test_documentation_url_and_scheme_only_literal_are_not_false_positive(self) -> None:
        self.write("README.md", "See http://example.test in the documentation.\n")
        self.write("helper.py", 'SCHEME = "http://"\n')

        result = analyze_repository(self.repository)

        self.assertNotIn("security.plain-http", {finding.rule_id for finding in result.findings})

    def test_invalid_utf8_is_marked_as_partial_without_crashing(self) -> None:
        invalid = self.repository / "broken.json"
        invalid.write_bytes(b"{\xff}\n")

        result = analyze_repository(self.repository)

        self.assertEqual(result.coverage["status"], "partial")
        self.assertEqual(result.coverage["text_files_omitted"], 1)

    def test_symlink_to_external_content_is_skipped_when_supported(self) -> None:
        outside = self.root / "outside.py"
        outside.write_text("eval('never inspect external content')\n", encoding="utf-8")
        link = self.repository / "external-link.py"
        try:
            os.symlink(outside, link)
        except (NotImplementedError, OSError):
            self.skipTest("Tworzenie symlinków nie jest dostępne w tym środowisku.")

        result = analyze_repository(self.repository)

        self.assertGreater(result.coverage["skipped"].get("link_or_reparse_point", 0), 0)
        self.assertNotIn("python.dynamic-execution", {finding.rule_id for finding in result.findings})

    def test_force_is_required_for_an_existing_report_directory(self) -> None:
        self.output.mkdir()
        (self.output / "other.txt").write_text("keep", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            validate_output_directory(self.repository, self.output)
        self.assertEqual(
            validate_output_directory(self.repository, self.output, force=True),
            self.output.resolve(),
        )


if __name__ == "__main__":
    unittest.main()
