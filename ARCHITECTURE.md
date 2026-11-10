# Architecture

The bounded JSONL parser normalizes rtl_433 event metadata, groups observations by model and declared device ID, calculates time span, message rate, median reported RSSI, and seen frequencies, and emits local reports. Unknown model values remain unknown; decoder assertions are not treated as verified protocol classifications. Input is capped at 25 MB and 100,000 records. No shared runtime dependency exists.
