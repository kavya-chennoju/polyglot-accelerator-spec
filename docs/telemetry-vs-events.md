# Telemetry vs Events

Polyglot is **not** a metrics firehose. The boundary:

- **Use `accelerator.heartbeat`** for periodic telemetry (utilization, memory, temperature, power, throttle reasons). Heartbeat events MUST arrive at least every 30 s and MUST NOT arrive faster than 1 Hz per device.
- **Use canonical fault events** for state changes that warrant human or agent attention.
- **Do NOT use Polyglot events** for high-frequency profiling.

DCGM, Prometheus, and vendor profilers remain the right tools for continuous counter scraping. Polyglot complements them; it does not replace them.

## Rule of thumb

| Signal | Where it belongs |
|---|---|
| GPU utilization sampled every 100 ms | DCGM / Prometheus |
| HBM bandwidth scraped every second | DCGM / Prometheus |
| Sustained NVLink replay errors crossing a threshold | Polyglot `interconnect_fault` event |
| Single Xid 31 occurrence | Polyglot `fatal_fault` event |
| Heartbeat snapshot every 30 s | Polyglot `heartbeat` event |
| Per-kernel SM activity profile | DCGM / nsys / vendor profilers |
| Confirmed silent data corruption hit | Polyglot `sdc_suspected` event |

If a driver finds itself wanting to emit an event more than once per second per device per `event_type`, the driver SHOULD aggregate the underlying signal or reconsider whether the data belongs in telemetry rather than events.

## What Polyglot adds on top of DCGM / Prometheus

| Capability | DCGM / Prometheus | Polyglot |
|---|---|---|
| High-frequency counter scraping | ✅ | ❌ (not the job) |
| Canonical fault vocabulary | ❌ (per-vendor) | ✅ |
| Vendor-neutral subscription queries | ❌ | ✅ |
| Vendor-neutral remediation RPCs | ❌ | ✅ |
| Safety / estop semantics | ❌ | ✅ |
| Agent-callable surface over MCP | ❌ | ✅ |

The two stacks compose: Prometheus does the counters; Polyglot does the events, discovery, and actuation.
