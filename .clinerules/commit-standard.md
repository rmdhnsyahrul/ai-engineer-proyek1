# Project Commit Standard

For every request to draft, create, amend, or review a commit in this
repository:

1. Read `docs/commit-convention.md` and `CONTRIBUTING.md`. Treat them as the
   authoritative commit specification.
2. Inspect `git status`, `git diff --check`, and `git diff --staged`.
3. Draft the message from staged changes and verification results that were
   actually observed, not from the original task description.
4. Follow the required structure:
   - A Conventional Commit subject of at most 72 characters.
   - A blank line after the subject.
   - Non-empty `Why:`, `What changed:`, and `How to verify:` sections in that
     order.
   - Optional `Notes / Tradeoffs:` and supported trailers when relevant.
5. Write durable commit artifacts in English.
6. Save the draft to a temporary file and validate it with:

   ```bash
   python3 scripts/check_commit_message.py <temporary-message-file>
   ```

7. Revise and revalidate the draft until the validator passes.
8. Never invent verification results. If a relevant check was not run, state
   that clearly instead of claiming success.
9. Do not create or amend the commit unless the user explicitly asks for that
   action.
