# Conformance Levels

A driver advertises one of three conformance levels in its identity manifest. The fleet service publishes each device's conformance level in `fleet.discover()` responses; consumers MAY restrict subscriptions to `level >= core`.

| Level | Requirements | Use case |
|---|---|---|
| **`core`** | Emits all REQUIRED events; implements all REQUIRED RPCs; passes the Core conformance suite. | Production accelerators in mixed-vendor fleets. |
| **`extended`** | `core` + emits all RECOMMENDED events + implements all RECOMMENDED RPCs. | Vendors with full telemetry and remediation surface area. |
| **`experimental`** | Emits or implements at least one canonical event or RPC but does not meet `core`. | Early-stage drivers; consumer code MAY filter them out by default. |

## How a driver advertises its level

The driver's identity manifest carries `conformance_level: "core" | "extended" | "experimental"`. The fleet service indexes this and exposes it as a discovery filter:

```python
fleet.discover("device_type=accelerator conformance_level>=core")
```

## What changes between levels

- **`core` → `extended`**: enables every RECOMMENDED event (`sdc_suspected`, `firmware_update_required`, `degraded_link_remediated`) and every RECOMMENDED RPC (`run_ecc_scrub`, `reset_device`, `set_power_cap`, `collect_dump`). Consumer code keying on the extended set will work; code keying only on `core` continues to work.
- **`experimental` → `core`**: requires passing every test in the conformance suite (see [Conformance Suite](conformance-suite.md)). This is the transition that matters for production fleets.

## Why have three levels?

Drivers ship at different maturity. A new vendor that has wired up `interconnect_fault` and `drain_device` but hasn't yet implemented `reset_link` is genuinely useful to early consumers — but consumers who can't tolerate missing RPCs should be able to filter them out. The conformance level is the explicit handshake.
