# Heinrich App — Claude Code Instructions

## Entry points & responsibilities

`services.py` is the sole public entry point for document generation. The entry
points (`app.py`, `cli.py`) call only `services.py` — never internal pipeline
modules.

Input validation and formatting of user-supplied arguments belongs in `input_args.py`,
not in `services.py`.

## Data protection

These paths are gitignored because they hold real customer data (Heinrich
Metallbau / RHI — master data, invoices, timesheets). Never read their contents
into context; use the listed substitute where one exists. This is also recorded
in Claude's memory for this project.

- `config.json`
- `RHI/`
- `templates/Vordruck.docx` — use `templates/Vordruck_sample.docx` instead

`notes/` is gitignored too but holds no customer data — it's the user's own
working notes and is always fine to read.

## Error handling

- Hard errors (file not found, invalid input): raise `ValueError` or `FileNotFoundError`
  and let them bubble up to the entry point.
- Non-fatal warnings and status messages for the UI: accumulate via `Messages.info()` /
  `.warning()` and return them — never use `print()`.
- Logging messages are in English; `Messages` entries shown to the user are in German.

## Models

- Immutable value objects use `@dataclass(frozen=True)`. Produce new objects instead of
  mutating.
- Domain models that map to Word template placeholders expose a `to_mapping()` method
  returning `dict[str, str]`.

## Comments and docstrings

- No inline comments unless the *why* is non-obvious (a hidden constraint, a workaround,
  a non-intuitive invariant). Never describe *what* the code does.
- Docstrings only for functions with a non-obvious contract or complex behavior (see
  `_replace_placeholder_across_runs`, `csv_rows_to_line_items` for examples of what
  warrants one).
- Short one-line module docstrings at the top of each file.

## Style conventions

- Language: code, docstrings and commit messages are in English; the decision log,
  `notes/` and the README are in German. (For `Messages` and logging see Error
  handling above.)
- Long files are divided by section separators: `# — Section name ————————————————`.
- Use relative imports within `src/backend/`.

## Git

Commit messages are a single line — imperative mood, no body, no trailer.
