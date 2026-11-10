import json
from pathlib import Path
import tempfile
import unittest

from ismobserver.core import analyze, normalize
from ismobserver.cli import main

ROW = {"time": "2026-11-09T12:00:00Z", "model": "lab-sensor", "id": 7, "freq": 433.92, "rssi": -52, "temperature_C": 21.5}


class Tests(unittest.TestCase):
    def test_normalize_inventory(self):
        self.assertEqual(normalize(ROW)["frequency_hz"], 433_920_000)
        report = analyze([ROW, {**ROW, "time": "2026-11-09T12:01:00Z"}], {"lab-sensor:7"})
        self.assertEqual(report["devices"][0]["message_count"], 2)
        self.assertTrue(report["devices"][0]["authorized"])

    def test_bounds(self):
        with self.assertRaises(ValueError):
            normalize({**ROW, "freq": 2400})
        with self.assertRaises(ValueError):
            normalize({**ROW, "time": "2026-11-09T12:00:00"})
        with self.assertRaises(ValueError):
            analyze([ROW] * 100001)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p / "input.jsonl").write_text(json.dumps(ROW) + "\n")
            self.assertEqual(main(["analyze", str(p / "input.jsonl"), "--output", str(p / "out.json"), "--csv", str(p / "out.csv")]), 0)
            self.assertEqual(json.loads((p / "out.json").read_text())["event_count"], 1)
            self.assertTrue((p / "out.csv").exists())


if __name__ == "__main__":
    unittest.main()
