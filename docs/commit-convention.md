# Commit as Documentation Convention

## Purpose

A commit is the smallest durable record of an engineering decision. Its
message must let a future developer or AI agent answer:

1. Why was this change necessary?
2. What behavior or architecture changed?
3. How was the result verified?
4. What constraints or follow-up work remain?

File contents describe the current state. Commit history explains how and why
that state evolved. Both are needed; commit messages do not replace source
documentation or tests.

## Subject

Use this form:

```text
<type>(<scope>): <imperative summary>
```

Rules:

- Maximum 72 characters.
- Use lowercase type and scope.
- Use an imperative summary: `add`, `prevent`, `stream`, not `added`.
- Do not end with a period.
- Use one language consistently. This repository uses English for durable
  artifacts even when planning discussions happen in Indonesian.

Allowed types:

| Type | Use |
| --- | --- |
| `feat` | New user-visible behavior |
| `fix` | Defect correction |
| `refactor` | Internal change without intended behavior change |
| `perf` | Performance improvement |
| `docs` | Documentation only |
| `test` | Test-only change |
| `build` | Build or packaging system |
| `ci` | Automation and continuous integration |
| `chore` | Maintenance not covered above |
| `revert` | Revert an earlier commit |

Choose a stable subsystem as the scope, for example `agent`, `api`, `rag`,
`streaming`, `config`, `deps`, `docs`, or `tests`.

## Body

Separate the subject and body with one blank line. The following sections are
required and must appear in this order.

### `Why:`

Document the problem, motivation, user impact, or roadmap context. Do not
repeat the subject.

### `What changed:`

Describe important behavior and design decisions. Mention files only when they
help locate a responsibility; avoid reproducing the diff line by line.

### `How to verify:`

Record reproducible commands and their expected outcomes. If a check could not
be run, state why instead of pretending it passed.

### `Notes / Tradeoffs:` (optional)

Record intentional limitations, rejected alternatives, compatibility impact,
or follow-up work.

## Trailers

Optional trailers make history machine-searchable:

```text
Roadmap: Agent service and streaming
Refs: #42
```

Use `Roadmap:` for a learning milestone or product capability. Use `Refs:` for
issues, pull requests, ADRs, or external documentation.

## Examples

### Valid feature commit

```text
feat(api): expose agent progress as server-sent events

Why:
HTTP clients need immediate feedback while the model executes CSV tools.

What changed:
- Added typed SSE events for tokens, tool calls, results, and completion.
- Added a bounded asynchronous agent loop with valid ToolMessage history.

How to verify:
- `uv run python -m unittest discover -s tests -v` -> all tests pass.
- `curl -N .../agent/stream` -> emits tool_call, token, and done events.

Notes / Tradeoffs:
- Requests are stateless; conversation memory is a later milestone.

Roadmap: Agent service and streaming
```

### Valid small fix

```text
fix(config): reject an empty agent prompt

Why:
An empty prompt creates an unnecessary provider request with no useful result.

What changed:
- Required at least one character in the API request model.

How to verify:
- POST an empty message -> HTTP 422.
```

### Invalid messages

```text
feat: tool calling
```

It says neither why the feature exists nor how to validate it.

```text
updated files
```

It lacks a valid type, scope, intent, and body.

```text
feat(agent): added streaming.
```

It is not imperative, ends with a period, and has no documentation sections.

## AI-assisted development

AI tools may create temporary snapshots for recovery. These are workspace
artifacts, not project history. Before sharing or merging a branch:

1. Inspect the complete diff and test results.
2. Group changes by engineering decision.
3. Squash or drop tool-generated checkpoint commits.
4. Write the final message from verified facts, not from the original prompt.
5. Never claim a command was run unless its result was observed.

## Existing repositories

Do not rewrite shared history merely to satisfy a newly adopted convention.
Apply the validator to new commits, then use normal pull requests to establish
the clean baseline. Rewrite only private, unshared branches when doing so makes
the review clearer.

The bootstrap script records the current `HEAD` in
`.commit-documentation-baseline`. CI validates commits after that revision, so
pre-adoption history remains intact. Commit the baseline file with the standard
and do not move it merely to bypass a failing commit.

A repository without commits has no baseline. In that case CI validates its
first commit directly, and subsequent pull requests use their normal revision
range.

Historical context can be added non-destructively with `git notes`, but notes
are not transferred by default and therefore do not replace good new commits.

## Reading history as context

Useful commands:

```bash
# Recent decisions with their complete documentation
git log -10 --format='%h %s%n%n%b%n---'

# Changes associated with a roadmap milestone
git log --all --grep='^Roadmap: Agent service and streaming$' --format=fuller

# Why a particular file evolved
git log --follow --format='%h %s%n%b' -- path/to/file

# Generate compact Markdown context from post-adoption commits
python3 scripts/export_commit_context.py --output /tmp/project-context.md
```

By default, the exporter starts after `.commit-documentation-baseline`. Pass
`--commit-range <revision-range>` when a task needs a narrower or older slice
of history.