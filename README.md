# ISMObserver

ISMObserver inventories authorized sensor observations from `rtl_433` JSONL exports. It normalizes frequency, decoder model, device ID, RSSI/SNR metadata, and selected sensor fields; computes message rate and observation history; and exports JSON/CSV reports. An optional JSON list of `model:id` values marks an authorized inventory. IDs are decoder metadata, not personal identities.

```sh
python3 -m ismobserver.cli hardware
python3 -m ismobserver.cli analyze authorized-rtl433.jsonl --authorized sensors.json --output report.json --csv inventory.csv
```

Supported frequency metadata is 300–320, 430–440, 863–870, or 902–928 MHz. This is a parser bound, not a transmission authorization. Regional regulations and actual receiver tuning limits govern collection. See [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), [HARDWARE.md](HARDWARE.md), [DEPENDENCIES.md](DEPENDENCIES.md), and [VALIDATION_REPORT.md](VALIDATION_REPORT.md).
