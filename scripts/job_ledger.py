#!/usr/bin/env python3
"""Normalize, deduplicate, and maintain the job-scout CSV ledger."""
import argparse, csv, hashlib, json, re, sys
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

FIELDS = ["job_id","first_seen","last_seen","company","title","employment_type","location","deadline","source","url","canonical_url","fit_score","fit_band","hard_gates","status","package_path","user_decision","submitted_at","notes"]
TRACKING_KEYS = {"fbclid", "gclid", "ref", "referrer", "source"}

def canonicalize_url(value):
    value = (value or "").strip()
    if not value:
        return ""
    parts = urlsplit(value)
    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if not k.lower().startswith("utm_") and k.lower() not in TRACKING_KEYS]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                       parts.path.rstrip("/") or "/", urlencode(kept), ""))

def normalized_text(value):
    return re.sub(r"[^0-9a-z가-힣]+", "", (value or "").casefold())

def dedupe_key(row):
    canonical = canonicalize_url(row.get("canonical_url") or row.get("url") or "")
    return "url:" + canonical if canonical else "text:" + normalized_text(row.get("company", "")) + "|" + normalized_text(row.get("title", ""))

def make_id(key):
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def read_ledger(path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return [{field: row.get(field, "") for field in FIELDS} for row in csv.DictReader(handle)]

def write_ledger(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

def iter_jsonl(value):
    handle = sys.stdin if value == "-" else open(value, encoding="utf-8")
    try:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f"line {number}: expected a JSON object")
            yield {str(k): "" if v is None else str(v) for k, v in item.items()}
    finally:
        if handle is not sys.stdin:
            handle.close()

def merge(path, input_path, today):
    rows = read_ledger(path)
    by_key = {dedupe_key(row): row for row in rows}
    protected = {"first_seen", "status", "package_path", "user_decision", "submitted_at"}
    for incoming in iter_jsonl(input_path):
        candidate = {field: incoming.get(field, "") for field in FIELDS}
        candidate["canonical_url"] = canonicalize_url(candidate["canonical_url"] or candidate["url"])
        key = dedupe_key(candidate)
        current = by_key.get(key)
        if current is None:
            candidate["job_id"] = candidate["job_id"] or make_id(key)
            candidate["first_seen"] = candidate["first_seen"] or today
            candidate["last_seen"] = today
            candidate["status"] = candidate["status"] or "discovered"
            by_key[key] = candidate
        else:
            for field in FIELDS:
                if field not in protected and candidate.get(field):
                    current[field] = candidate[field]
            current["last_seen"] = today
            current["canonical_url"] = canonicalize_url(current["canonical_url"] or current["url"])
    write_ledger(path, sorted(by_key.values(), key=lambda row: (row["first_seen"], row["company"], row["title"])))

def check(path):
    rows, ids, keys, errors = read_ledger(path), set(), set(), []
    for number, row in enumerate(rows, 2):
        key = dedupe_key(row)
        if not row["job_id"]:
            errors.append(f"row {number}: missing job_id")
        elif row["job_id"] in ids:
            errors.append(f"row {number}: duplicate job_id {row['job_id']}")
        if key in keys:
            errors.append(f"row {number}: duplicate posting {key}")
        ids.add(row["job_id"]); keys.add(key)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {len(rows)} rows")
    return 0

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init").add_argument("ledger")
    merge_parser = sub.add_parser("merge")
    merge_parser.add_argument("ledger")
    merge_parser.add_argument("--input", required=True, help="JSONL file or -")
    merge_parser.add_argument("--date", default=date.today().isoformat())
    sub.add_parser("check").add_argument("ledger")
    args = parser.parse_args()
    path = Path(args.ledger)
    if args.command == "init":
        if not path.exists(): write_ledger(path, [])
        return 0
    if args.command == "merge":
        merge(path, args.input, args.date)
        return 0
    return check(path)

if __name__ == "__main__":
    raise SystemExit(main())
