# Required Event Vocabulary

A `core` driver MUST emit the following canonical event types, with full schema conformance, whenever the underlying condition is detected.

## The required set

| Event type | When to emit | `fault_class` label |
|---|---|---|
| `accelerator.interconnect_fault` | Any persistent or recurring failure on an intra-node or inter-node link (NVLink, XGMI, NeuronLink, IB / RoCE, PCIe AER for fabric-relevant lanes). | `interconnect` |
| `accelerator.ecc_uncorrectable` | Any uncorrectable ECC / DBE event in HBM / SRAM / cache. | `memory` |
| `accelerator.ecc_correctable_burst` | Correctable ECC rate exceeding the per-device burst threshold the driver defines. | `memory` |
| `accelerator.thermal_throttle` | Sustained throttle attributable to thermal limits. | `thermal` |
| `accelerator.power_throttle` | Sustained throttle attributable to power cap. | `thermal` |
| `accelerator.fatal_fault` | Vendor-reported fatal hardware fault (Xid 79 "fell off bus", AMD GPU hang, Habana firmware fault, Trainium fault register set). | `firmware` |
| `accelerator.heartbeat` | Periodic (≥ every 30s) liveness with the latest snapshot of utilization, mem, temp, power. Used by the fleet service to detect dead drivers. | `lifecycle` |

## Recommended (extended) events

| Event type | When to emit |
|---|---|
| `accelerator.sdc_suspected` | Driver-side heuristic detects probable silent data corruption (numerical drift, golden-test mismatch). |
| `accelerator.firmware_update_required` | Firmware mismatch vs. fleet-declared minimum. |
| `accelerator.degraded_link_remediated` | After a `run_link_diagnostic` clears an `interconnect_fault`. Closes the loop for consumers. |

## Event payload conformance

Every emitted event MUST validate against the JSON Schema at:

```
https://schemas.polyglot.org/accelerator/<schema_version>/<event_type>.json
```

REQUIRED top-level fields on every event:

| Field | Type | Notes |
|---|---|---|
| `event_type` | string | Canonical event type. |
| `schema_version` | string | MUST be present in the driver's `schema_versions` manifest. |
| `schema_uri` | string | Resolvable URI to the JSON Schema file. |
| `severity` | enum | `info` / `degraded` / `critical`. |
| `confidence` | float in `[0.0, 1.0]` | Driver's confidence in its classification. |
| `device` | object | Echoes manifest identity fields. |
| `topology` | object | MUST include all topology fields relevant to the event (`link_type` for interconnect events, etc.). |
| `vendor_evidence` | array of objects | Raw vendor signals. See [Extension Points](extensions.md). |
| `normalized_effect` | object | Canonical impact. See below. |
| `recommended_actions` | array of strings | RPC names the driver considers safe. MUST be a subset of the driver's exposed RPCs. |
| `disallowed_actions` | array of strings | RPC names the driver explicitly forbids in response to this event. |
| `lifecycle` | enum | `transient` / `degraded` / `fatal`. |
| `labels` | object | See [Labels](labels.md). |

## `normalized_effect` block

| Field | Values |
|---|---|
| `communication_path` | `ok` / `degraded` / `failed` |
| `compute_path` | `ok` / `degraded` / `failed` |
| `memory_integrity` | `ok` / `degraded` / `failed` |
| `bandwidth_impact` | `none` / `possible` / `probable` / `confirmed` |
| `job_correctness_risk` | `none` / `unknown` / `low` / `medium` / `high` |
| `job_performance_risk` | `none` / `low` / `medium` / `high` |

Drivers MUST populate every field. `unknown` is permitted on `job_correctness_risk` only — all others have factual answers the driver SHOULD be able to determine.

## Emission semantics

- Drivers MUST debounce repeated events for the same underlying condition. A storm of identical NVLink replay errors MUST collapse into one `interconnect_fault` event with periodic refresh (suggested: every 30s while the condition persists).
- Drivers MUST emit a closing event when the condition clears: either `accelerator.degraded_link_remediated` (extended) or a final `interconnect_fault` with `severity: info` and `normalized_effect.communication_path: ok`.
- Drivers MUST NOT emit events asynchronously to underlying signals at a rate faster than 1 Hz per event_type per device.

## Full example

```json
{
  "event_type":      "accelerator.interconnect_fault",
  "schema_version":  "2026-06-01",
  "schema_uri":      "https://schemas.polyglot.org/accelerator/2026-06-01/interconnect_fault.json",
  "severity":        "degraded",
  "confidence":      0.92,
  "lifecycle":       "degraded",
  "device": {
    "vendor":    "nvidia",
    "model":     "H100",
    "device_id": "gpu-042",
    "host_id":   "node-17",
    "tenant":    "training-prod"
  },
  "topology": {
    "link_type":      "nvlink",
    "local_port":     "nvlink3",
    "peer_device_id": "gpu-043",
    "fabric_domain":  "rack12-nvsw02"
  },
  "vendor_evidence": [
    { "source": "dcgm",       "code": "NVLINK_REPLAY_ERRORS", "value": 18492, "threshold": 1000 },
    { "source": "nvidia-xid", "code": "XID_74",               "message": "NVLink error" }
  ],
  "normalized_effect": {
    "communication_path":   "degraded",
    "compute_path":         "ok",
    "memory_integrity":     "ok",
    "bandwidth_impact":     "probable",
    "job_correctness_risk": "unknown",
    "job_performance_risk": "high"
  },
  "recommended_actions": ["run_link_diagnostic", "drain_device"],
  "disallowed_actions":  ["reset_link_without_drain", "estop"],
  "labels": {
    "fault_class":    "interconnect",
    "fault_domain":   "link",
    "stability":      "stable",
    "evidence_grade": "direct"
  }
}
```
