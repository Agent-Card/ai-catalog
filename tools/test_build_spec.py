import json
import tempfile
import unittest
from pathlib import Path

import markdown

from build_spec import build_document, build_section_tree, render_sections


class PublicationStatusTests(unittest.TestCase):
    def test_build_uses_source_status_without_generated_draft_notice(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "spec.md"
            output = root / "index.html"
            config = root / "config.json"
            source.write_text(
                "# Status of This Document\n\n"
                "Ready for **implementation feedback**.\n\n"
                "# Introduction\n\nSpecification content.\n",
                encoding="utf-8",
            )
            config.write_text(
                json.dumps({"title": "Test Specification", "abstract": "Test abstract."}),
                encoding="utf-8",
            )

            build_document(source, output, config)
            document = output.read_text(encoding="utf-8")

        self.assertEqual(document.count('id="sotd"'), 1)
        self.assertIn('class="introductory override" id="sotd"', document)
        self.assertEqual(document.count("<h2>Status of This Document</h2>"), 1)
        self.assertIn("Ready for <strong>implementation feedback</strong>.", document)
        self.assertNotIn("This is a draft document", document)
        self.assertIn('<section id="introduction">', document)

    def test_nested_status_heading_remains_an_ordinary_section(self):
        sections = build_section_tree(
            "# Introduction\n\n## Status of This Document\n\nNested discussion.\n", []
        )

        document = render_sections(markdown.Markdown(), sections)

        self.assertIn('<section id="status-of-this-document">', document)
        self.assertNotIn('id="sotd"', document)


if __name__ == "__main__":
    unittest.main()
