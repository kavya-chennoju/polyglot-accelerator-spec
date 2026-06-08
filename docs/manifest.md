# Identity Manifest

Every driver MUST register an identity manifest at startup. The manifest is queryable via `fleet.discover()` and is the source of truth for the device labels the fleet service applies to events from that device.

The manifest is **identity-only**. Topology (which port, which peer, which fabric_domain a fault touches) is *per-event* — drivers populate the event-level [`topology`](events.md) block when emitting. Drivers internally know their fabric position; they don't republish a static topology block in the manifest.

## Required fields

| Field | Type | Notes |
|---|---|---|
| `device_type` | string, literal `"accelerator"` | Identifies this as an accelerator driver. MUST NOT be omitted or aliased. |
| `vendor` | string | Lowercase: `nvidia`, `amd`, `intel`, `aws_neuron`, `google_tpu`, `meta_mtia`, `<vendor>`. New vendors require an RFC. |
| `model` | string | Vendor-canonical SKU. Examples: `H100`, `MI300X`, `Gaudi3`, `Trainium2`, `TPUv5p`. |
| `device_id` | string | Operator-assigned, fleet-unique. MUST be stable across restarts. |
| `host_id` | string | Operator-assigned host identity. MUST match the host's `mhp-fleet-service` registration. |
| `fw_version` | string | Driver / firmware version reported by the vendor SDK. |
| `conformance_level` | enum | One of `core` / `extended` / `experimental`. |
| `schema_versions` | array of strings | All `polyglot-accelerator` contract versions this driver can emit (e.g. `["2026-06-01"]`). MUST contain at least one stable version. |

## Optional fields

| Field | When to set |
|---|---|
| `tenant` | If the device is scoped to a specific tenant (multi-tenant fleets). |
| `labels.<vendor>.*` | Vendor-specific diagnostic labels. Non-portable; consumer code MUST NOT depend on them. |
| `hw_revision`, `serial`, `power_cap_w`, `mem_total_gb` | When known and useful for fleet-wide queries. |

## Example

```json
{
  "device_type":       "accelerator",
  "vendor":            "nvidia",
  "model":             "H100",
  "device_id":         "gpu-042",
  "host_id":           "node-17",
  "fw_version":        "535.183.06",
  "conformance_level": "core",
  "schema_versions":   ["2026-06-01"],
  "tenant":            "training-prod"
}
```

## Why no static topology block here?

Topology context belongs to *events*, not to the device's identity. A fault doesn't just hit `gpu-042` — it hits `gpu-042` on a specific NVLink port to a specific peer in a specific fabric domain. Those details are situational and only meaningful in the context of the event that surfaced them. Putting them per-event keeps the contract minimal at registration time, lets the driver decide which subset of topology context to attach per event, and avoids stale state when topology shifts (e.g. dynamic NVSwitch repartitioning).

The driver's internal knowledge of fabric position is what feeds the event-level [`topology`](events.md#full-example) block when a fault is emitted. That's the contract surface; the manifest stays identity-only.
