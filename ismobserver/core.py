from collections import defaultdict
from datetime import datetime
import json
import math
from statistics import median

BANDS = [(300_000_000, 320_000_000, "315 MHz"), (430_000_000, 440_000_000, "433 MHz"),
         (863_000_000, 870_000_000, "868 MHz"), (902_000_000, 928_000_000, "915 MHz")]


def normalize(row: dict) -> dict:
    if not isinstance(row, dict) or len(json.dumps(row)) > 8192:
        raise ValueError("invalid rtl_433 row")
    stamp = row.get("time") or row.get("timestamp")
    if not isinstance(stamp, str):
        raise ValueError("timestamp required")
    dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp requires timezone")
    freq = row.get("freq") or row.get("frequency_hz")
    if freq is not None:
        freq = float(freq)
        # rtl_433 commonly emits frequency in MHz; preserve explicit unit conversion.
        if freq < 10_000:
            freq *= 1_000_000
        if not any(low <= freq <= high for low, high, _ in BANDS):
            raise ValueError("frequency outside supported observation bands")
    model = str(row.get("model", "unknown"))[:128]
    device_id = str(row.get("id", row.get("device_id", "unknown")))[:128]
    rssi = row.get("rssi")
    if rssi is not None:
        rssi = float(rssi)
        if not -200 <= rssi <= 50:
            raise ValueError("invalid RSSI metadata")
    snr = row.get("snr")
    if snr is not None:
        snr = float(snr)
        if not math.isfinite(snr) or not -100 <= snr <= 100:
            raise ValueError("invalid SNR metadata")
    return {"timestamp": dt.isoformat(), "model": model, "device_id": device_id,
            "frequency_hz": freq, "rssi_metadata": rssi, "snr_metadata": snr,
            "protocol": str(row.get("protocol", model))[:128],
            "decoder_confidence": "decoder asserted; not independently verified",
            "sensor_metadata": {key: row[key] for key in ("temperature_C", "humidity", "battery_ok", "channel") if key in row}}


def analyze(rows: list[dict], authorized: set[str] | None = None) -> dict:
    if not isinstance(rows, list) or len(rows) > 100_000:
        raise ValueError("too many events")
    groups = defaultdict(list)
    for row in rows:
        event = normalize(row)
        groups[(event["model"], event["device_id"])].append(event)
    devices, indicators = [], []
    for (model, ident), events in groups.items():
        events.sort(key=lambda x: x["timestamp"])
        start = datetime.fromisoformat(events[0]["timestamp"])
        end = datetime.fromisoformat(events[-1]["timestamp"])
        duration = (end - start).total_seconds()
        rate = (len(events) - 1) / duration * 3600 if duration > 0 else None
        rssis = [x["rssi_metadata"] for x in events if x["rssi_metadata"] is not None]
        key = f"{model}:{ident}"
        devices.append({"inventory_key": key, "authorized": key in authorized if authorized is not None else None,
                        "first_seen": events[0]["timestamp"], "last_seen": events[-1]["timestamp"],
                        "message_count": len(events), "observed_rate_per_hour": rate,
                        "median_rssi_metadata": median(rssis) if rssis else None,
                        "frequencies_hz": sorted({x["frequency_hz"] for x in events if x["frequency_hz"] is not None}),
                        "last_sensor_metadata": events[-1]["sensor_metadata"]})
        if rate is not None and rate > 3600:
            indicators.append({"inventory_key": key, "indicator": "high observed message rate", "confidence": "low"})
    return {"devices": sorted(devices, key=lambda x: x["inventory_key"]), "indicators": indicators,
            "event_count": len(rows), "interpretation": "decoder metadata and observed events; IDs are not people or verified physical identities"}
