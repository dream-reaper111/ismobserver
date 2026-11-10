from pathlib import Path
import shutil


def capabilities() -> list[dict]:
    adapters = sorted(p.name for p in Path("/sys/class/bluetooth").glob("hci*"))
    return [
        {"kind": "local_ble_adapter", "device": adapters or None, "available": False,
         "frequency_range_hz": [2400000000, 2483500000] if adapters else None,
         "sample_rate_limits": None, "operations": [], "required_permissions": ["BlueZ access"],
         "driver_dependencies": ["BlueZ"], "detail": "not integrated"},
        {"kind": "dedicated_ble_sniffer", "device": None, "available": False,
         "frequency_range_hz": None, "sample_rate_limits": None, "operations": [],
         "required_permissions": [], "driver_dependencies": [], "detail": "not integrated"},
        {"kind": "receive_only_sdr", "device": None, "available": False,
         "frequency_range_hz": None, "sample_rate_limits": None, "operations": [],
         "required_permissions": ["receiver access"], "driver_dependencies": ["rtl_433", "RTL-SDR driver"],
         "detail": f"rtl_433 executable {'found' if shutil.which('rtl_433') else 'absent'}; receiver not verified"},
        {"kind": "offline_capture_import", "device": "rtl_433 JSONL", "available": True,
         "frequency_range_hz": None, "sample_rate_limits": None, "operations": ["import", "analyze"],
         "required_permissions": ["file read"], "driver_dependencies": ["Python 3.12"],
         "detail": "offline analysis"},
    ]
