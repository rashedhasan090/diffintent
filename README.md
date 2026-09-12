# diffintent

**Offline CLI that classifies unified-diff hunks by change intent** — tests, docs, deps, config, CI, generated, or code — so you can skim a PR faster or feed an agent only the slices it needs.

## Why this is novel

Most diff tools show *what* changed line-by-line. Agent/context tools pack *how much* text fits. `diffintent` answers a different question: **what kind of change is this?**

It is **not**:

| Tool | What it does instead |
|------|----------------------|
| [sandclock](https://github.com/rashedhasan090/sandclock) | Timeboxes a command and reports filesystem delta |
| [rippleguard](https://github.com/rashedhasan090/rippleguard) | Maps language/CI capability surfaces |
| [tokpack](https://github.com/rashedhasan090/tokpack) | Packs files under a token budget |
| [toolflow](https://github.com/rashedhasan090/toolflow) | Turns agent tool-call JSONL into Mermaid |
| [hedgescope](https://github.com/rashedhasan090/hedgescope) | Flags hedging / overclaim in research drafts |
| [hushdiff](https://github.com/rashedhasan090/hushdiff) | Masks secret-shaped tokens in diffs |
| [runseal](https://github.com/rashedhasan090/runseal) | Content-addressed receipts for command runs |

`diffintent` only **parses** a unified diff. It never applies patches or runs shell commands.

## Install

```bash
git clone https://github.com/rashedhasan090/diffintent.git
cd diffintent
pip install -e .
```

Or run without installing:

```bash
PYTHONPATH=src python3 -m diffintent examples/sample.diff
```

## Usage

```bash
# From a file
diffintent examples/sample.diff

# From git
git diff main...HEAD | diffintent -
git show --format= | diffintent -

# JSON for agents / scripts
diffintent examples/sample.diff --json

# Only tests + docs
diffintent examples/sample.diff --only tests --only docs
```

### Demo

```text
$ PYTHONPATH=src python3 -m diffintent examples/sample.diff
files=6  +23/-1  hunks=6
by intent: tests:1  docs:1  deps:1  config:1  ci:1  code:1

  [code     ] +5   /-1     src/app.py
  [tests    ] +4   /-0     tests/test_app.py (new)
  [docs     ] +3   /-0     README.md
  [deps     ] +1   /-0     requirements.txt
  [ci       ] +8   /-0     .github/workflows/ci.yml (new)
  [config   ] +2   /-0     .env.example (new)
```

## Categories

| Category | Typical paths |
|----------|----------------|
| `tests` | `tests/`, `*_test.py`, `*.spec.ts` |
| `docs` | `README*`, `*.md`, `docs/` |
| `deps` | `requirements*.txt`, lockfiles, `package.json`, `go.mod` |
| `config` | `.env*`, `Dockerfile`, `*.yml` (non-workflow), `.*rc` |
| `ci` | `.github/workflows/*`, `.gitlab-ci.yml` |
| `generated` | `dist/`, `*.min.js`, `*_pb2.py` |
| `code` | everything else |

Each file also gets light **risk hints** for review (`delete-only`, `delete-heavy`, `large-add`, `binary`) — review aids, not vulnerability findings.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Analysis succeeded |
| 2 | Could not read input / empty diff |

## License

MIT
