import unittest

from scripts.check_commit_message import validate_commit_message


VALID_MESSAGE = """feat(agent): stream tool events over SSE

Why:
API clients need progress while an analysis tool is running.

What changed:
- Added typed tool and token events.

How to verify:
- `python -m unittest` -> all tests pass.

Notes / Tradeoffs:
- Requests remain stateless.

Roadmap: Agent service and streaming
"""


class CommitMessageTests(unittest.TestCase):
    def test_accepts_documentation_grade_message(self) -> None:
        self.assertEqual(validate_commit_message(VALID_MESSAGE), [])

    def test_ignores_git_template_comments(self) -> None:
        message = VALID_MESSAGE + "\n# template guidance\n"
        self.assertEqual(validate_commit_message(message), [])

    def test_rejects_subject_without_conventional_type(self) -> None:
        errors = validate_commit_message(VALID_MESSAGE.replace("feat(agent):", "update:"))
        self.assertTrue(any("subject must match" in error for error in errors))

    def test_rejects_subject_longer_than_72_characters(self) -> None:
        message = VALID_MESSAGE.replace(
            "feat(agent): stream tool events over SSE",
            "feat(agent): " + "a" * 60,
        )
        errors = validate_commit_message(message)
        self.assertTrue(any("maximum is 72" in error for error in errors))

    def test_rejects_missing_required_section(self) -> None:
        message = VALID_MESSAGE.replace("How to verify:", "Verification:")
        errors = validate_commit_message(message)
        self.assertIn("missing required section 'How to verify:'", errors)

    def test_rejects_empty_required_section(self) -> None:
        message = VALID_MESSAGE.replace(
            "Why:\nAPI clients need progress while an analysis tool is running.",
            "Why:",
        )
        errors = validate_commit_message(message)
        self.assertIn("section 'Why:' must contain documentation", errors)

    def test_rejects_missing_blank_line_after_subject(self) -> None:
        errors = validate_commit_message(VALID_MESSAGE.replace("SSE\n\nWhy:", "SSE\nWhy:"))
        self.assertIn("add one blank line between the subject and body", errors)

    def test_accepts_git_generated_merge_and_fixup_messages(self) -> None:
        self.assertEqual(validate_commit_message("Merge branch 'main'"), [])
        self.assertEqual(validate_commit_message("fixup! feat(agent): add loop"), [])

    def test_rejects_sections_in_the_wrong_order(self) -> None:
        message = VALID_MESSAGE.replace(
            "Why:\nAPI clients need progress while an analysis tool is running.\n\n"
            "What changed:\n- Added typed tool and token events.",
            "What changed:\n- Added typed tool and token events.\n\n"
            "Why:\nAPI clients need progress while an analysis tool is running.",
        )
        errors = validate_commit_message(message)
        self.assertTrue(any("must appear in order" in error for error in errors))


if __name__ == "__main__":
    unittest.main()