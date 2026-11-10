import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

from .core import analyze
from .hardware import capabilities


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ismobserver")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("hardware")
    run = sub.add_parser("analyze")
    run.add_argument("input", type=Path)
    run.add_argument("--authorized", type=Path)
    run.add_argument("--output", type=Path)
    run.add_argument("--csv", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "hardware":
            print(json.dumps(capabilities(), indent=2))
            return 0
        if args.input.stat().st_size > 25_000_000:
            raise ValueError("input exceeds 25 MB")
        data = args.input.read_bytes()
        lines = data.decode().splitlines()
        if any(len(x) > 8192 for x in lines):
            raise ValueError("line exceeds limit")
        authorized = None
        if args.authorized:
            if args.authorized.stat().st_size > 100_000:
                raise ValueError("authorized inventory exceeds limit")
            values = json.loads(args.authorized.read_text())
            if not isinstance(values, list):
                raise ValueError("authorized inventory must be a list")
            authorized = set(values)
        report = analyze([json.loads(x) for x in lines if x.strip()], authorized)
        report["source_sha256"] = hashlib.sha256(data).hexdigest()
        if args.csv:
            with args.csv.open("w", newline="") as stream:
                fields = ["inventory_key", "authorized", "first_seen", "last_seen", "message_count", "observed_rate_per_hour", "median_rssi_metadata", "frequencies_hz", "last_sensor_metadata"]
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(report["devices"])
        result = json.dumps(report, indent=2) + "\n"
        if args.output:
            args.output.write_text(result)
        else:
            print(result, end="")
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"ismobserver: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
