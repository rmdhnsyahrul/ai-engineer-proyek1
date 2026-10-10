# Commit Workflow: Start to End

This guide shows how to create, validate, publish, and reuse a documented
commit. Read the [commit convention](commit-convention.md) for the complete
message specification.

## Complete flow

```mermaid
flowchart TD
    start([Start: one engineering decision is complete])
    review[Review the diff and run focused checks]
    stage[Stage only files for that decision]
    commit[Run git commit]
    template[Git opens the .gitmessage template]
    write[Write subject, Why, What changed, and How to verify]
    hook[Git runs the commit-msg hook]
    validate[Validator checks .git/COMMIT_EDITMSG]
    valid{Message valid?}
    reject[Commit is rejected and errors are printed]
    created[Commit is created]
    push[Push the branch]
    ci[GitHub Actions validates the commit range]
    ci_valid{All messages valid?}
    repair[Amend or rebase invalid commits]
    done([End: documented history is ready for reuse])

    start --> review --> stage --> commit --> template --> write --> hook
    hook --> validate --> valid
    valid -- No --> reject --> write
    valid -- Yes --> created --> push --> ci --> ci_valid
    ci_valid -- No --> repair --> push
    ci_valid -- Yes --> done
```

## 1. Install the standard once

From this repository, configure the current repository with:

```bash
./scripts/apply-git-standards.sh .
```

The script:

1. Installs the template, validator, context exporter, convention, and CI
   workflow.
2. Records the existing `HEAD` in `.commit-documentation-baseline` when the
   repository already has commits.
3. Configures `.gitmessage` as the local Git commit template.
4. Installs an executable `.git/hooks/commit-msg` hook.

The bootstrap flow is:

```mermaid
flowchart LR
    repo[Git repository]
    bootstrap[apply-git-standards.sh]
    files[Install shared standard files]
    baseline[Record pre-adoption HEAD]
    template[Configure commit.template]
    hook[Install commit-msg hook]
    ready([Ready to commit])

    repo --> bootstrap
    bootstrap --> files --> ready
    bootstrap --> baseline --> ready
    bootstrap --> template --> ready
    bootstrap --> hook --> ready
```

Verify the installation:

```bash
git config --local --get commit.template
test -x .git/hooks/commit-msg && echo "commit-msg hook is active"
```

The expected template value is `.gitmessage`.

### Optional pre-commit installation

Teams already using pre-commit can install the equivalent configured hook:

```bash
uv sync --dev
uv run pre-commit install --hook-type commit-msg
```

Both hook options invoke `scripts/check_commit_message.py`. One working
`commit-msg` hook is sufficient; the bootstrap hook does not require the
`pre-commit` package at commit time.

## 2. Prepare one commit

Review the work, run its focused checks, and stage one engineering decision:

```bash
git diff --check
git diff
uv run python -m unittest discover -s tests -v
git add path/to/implementation.py path/to/test.py
git diff --staged
```

Implementation, focused tests, and directly related documentation should
normally stay together. Unrelated refactors or dependency updates should use
separate commits.

## 3. Create an interactive commit

Run:

```bash
git commit
```

Git opens `.gitmessage` in the configured editor. Replace the commented
guidance with verified facts:

```text
feat(agent): stream tool execution events over SSE

Why:
HTTP clients need progress while the model executes CSV tools.

What changed:
- Added typed SSE events for tool calls, results, tokens, and completion.
- Preserved valid tool-message history in the bounded agent loop.

How to verify:
- `uv run python -m unittest discover -s tests -v` -> all tests pass.

Notes / Tradeoffs:
- Requests remain stateless.

Roadmap: Agent service and streaming
```

Save and close the editor. Git then invokes the validator automatically.

## 4. Create a non-interactive commit

Automation and coding agents can write the same message to a temporary file:

```bash
cat > /tmp/commit-message.txt <<'EOF'
docs(commits): explain the end-to-end commit workflow

Why:
Contributors need an operational guide in addition to the message specification.

What changed:
- Added setup, local validation, CI, and recovery flows.
- Added Mermaid diagrams for the complete lifecycle.

How to verify:
- Review the rendered Markdown -> all diagrams and links are readable.

Roadmap: Commit as documentation
EOF

python3 scripts/check_commit_message.py /tmp/commit-message.txt
git commit -F /tmp/commit-message.txt
rm /tmp/commit-message.txt
```

The explicit validator call gives early feedback. `git commit` still runs the
hook and validates the final message again.

## 5. Understand local validation

```mermaid
sequenceDiagram
    actor Developer
    participant Git
    participant Hook as commit-msg hook
    participant Validator as check_commit_message.py

    Developer->>Git: git commit
    Git-->>Developer: Open .gitmessage in editor
    Developer->>Git: Save commit message
    Git->>Hook: Pass .git/COMMIT_EDITMSG
    Hook->>Validator: Validate message file
    alt Message is valid
        Validator-->>Git: Exit 0
        Git-->>Developer: Create commit
    else Message is invalid
        Validator-->>Git: Exit 1 with errors
        Git-->>Developer: Abort commit for correction
    end
```

The validator requires:

- A Conventional Commit subject no longer than 72 characters.
- An allowed type: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`,
  `ci`, `chore`, or `revert`.
- A blank line after the subject.
- Non-empty `Why:`, `What changed:`, and `How to verify:` sections in that
  order.

`Notes / Tradeoffs:` and supported trailers are optional. Git-generated merge,
revert, fixup, and squash subjects are exempt.

## 6. Correct a rejected message

The validator prints every detected problem. Correct the message and retry:

```bash
git commit
```

If a bad commit already exists locally, amend it:

```bash
git commit --amend
```

For multiple private commits, use an interactive rebase and mark the affected
commits for rewording:

```bash
git rebase -i <base-commit>
```

Do not rewrite commits other people may already use. Use `--no-verify` only
when the hook itself is broken, not to bypass a documentation error.

## 7. Push and pass CI

The GitHub Actions workflow selects a commit range and runs:

```bash
python3 scripts/check_commit_message.py --commit-range '<range>'
```

```mermaid
flowchart TD
    event[Pull request, main push, or reusable workflow]
    input{Explicit range supplied?}
    baseline{Baseline file exists?}
    pr{Pull request?}
    existing{Existing branch push?}
    explicit[Use supplied range]
    adopted[Use baseline through HEAD]
    pr_range[Use pull request base through HEAD]
    push_range[Use previous SHA through HEAD]
    first[Use HEAD for the first push]
    validator[Validate every commit in the selected range]
    result{All messages valid?}
    fail[Fail the CI job]
    pass([Pass the CI job])

    event --> input
    input -- Yes --> explicit --> validator
    input -- No --> baseline
    baseline -- Yes --> adopted --> validator
    baseline -- No --> pr
    pr -- Yes --> pr_range --> validator
    pr -- No --> existing
    existing -- Yes --> push_range --> validator
    existing -- No --> first --> validator
    validator --> result
    result -- No --> fail
    result -- Yes --> pass
```

The baseline preserves pre-adoption history without rewriting it. Do not move
the baseline merely to hide a failing new commit.

## 8. Reuse commits as development context

After documented commits accumulate, export them as compact Markdown:

```bash
python3 scripts/export_commit_context.py --output /tmp/project-context.md
```

By default, the exporter includes commits after
`.commit-documentation-baseline`. Select a narrower range when needed:

```bash
python3 scripts/export_commit_context.py \
  --commit-range 'main..HEAD' \
  --output /tmp/branch-context.md
```

The resulting document contains each commit hash, subject, and body, making
the verified decision history available as starting context for future
developers and AI agents.

## Command summary

```bash
# Install once
./scripts/apply-git-standards.sh .

# Prepare and commit
git diff --check
git add <files>
git diff --staged
git commit

# Validate the complete post-adoption history
python3 scripts/check_commit_message.py \
  --commit-range "$(cat .commit-documentation-baseline)..HEAD"

# Export history as reusable context
python3 scripts/export_commit_context.py --output /tmp/project-context.md
```