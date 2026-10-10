# Contributing

This repository treats every commit as durable engineering documentation.
Someone reading `git log` should understand why a change exists, what changed,
how it was verified, and which limitations remain without first reading the
entire repository.

## One-time setup

Install development dependencies and the commit-message hook:

```bash
uv sync --dev
uv run pre-commit install --hook-type commit-msg
git config --local commit.template .gitmessage
```

Alternatively, run the repository bootstrap script:

```bash
./scripts/apply-git-standards.sh .
```

## Required commit format

Use Conventional Commits for the subject and documentation sections for the
body:

```text
feat(agent): stream tool execution events over SSE

Why:
The CLI-only agent could not expose progress to HTTP clients.

What changed:
- Added a reusable agent loop and an SSE endpoint.
- Preserved tool calls and results as typed events.

How to verify:
- `uv run python -m unittest discover -s tests -v` -> all tests pass.

Notes / Tradeoffs:
- Conversation memory remains outside this milestone.

Roadmap: Agent service and streaming
```

The required sections are `Why:`, `What changed:`, and `How to verify:`.
`Notes / Tradeoffs:` and trailers are optional. See
[`docs/commit-convention.md`](docs/commit-convention.md) for the complete
specification.

## Commit boundaries

- Keep one architectural or behavioral decision per commit.
- Include implementation, focused tests, and relevant documentation together.
- Do not mix unrelated formatting, dependency upgrades, or generated files.
- Do not commit temporary AI checkpoints such as `Agent host session`,
  `cline checkpoint`, or `WIP`. Squash them into a documented commit first.
- Prefer a small sequence of complete commits over one broad snapshot.

## Before committing

1. Review `git diff --check` and `git diff --staged`.
2. Run the focused tests documented in `How to verify:`.
3. Stage only files belonging to the same decision.
4. Run `git commit`; the configured template opens automatically.

Use `git commit --no-verify` only when the hook itself is broken. Explain the
bypass in the pull request and fix the validator in the same change series.

## Reusing history as development context

Generate compact Markdown containing documented post-adoption commits:

```bash
python3 scripts/export_commit_context.py --output /tmp/project-context.md
```

Future development can start with this context and then inspect only the files
named by the relevant decisions.