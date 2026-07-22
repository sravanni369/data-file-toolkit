# data-file-toolkit

Convert and validate tabular data files (CSV ↔ JSON) from the command line. Standard library only. Every function tested.

## What it does

- **csv2json** — read a CSV, coerce types (int → float → string → null), write JSON
- **json2csv** — flatten a JSON array of objects back to CSV
- **validate** — check required columns exist and are non-empty; report bad rows with line numbers instead of crashing

## Usage

```bash
python -m toolkit csv2json input.csv output.json
python -m toolkit json2csv input.json output.csv
python -m toolkit validate input.csv --require member_id age premium
```

## Run tests

```bash
python -m unittest discover tests -v
```

## Design notes

- Bad rows never abort a batch: they are collected and reported (line-numbered), the rest of the file still processes.
- Type coercion is best-effort and explicit — `"42"` becomes `42`, `"4.2"` becomes `4.2`, `""` becomes `null`, anything else stays a string.
- No third-party dependencies, so it runs anywhere Python 3.10+ runs.

## Tech

Python 3.10+, `csv`, `json`, `argparse`, `unittest`. CI runs the test suite on every push.

---
Contact: sravannicareerv@gmail.com | linkedin.com/in/sravani-p-212899272
