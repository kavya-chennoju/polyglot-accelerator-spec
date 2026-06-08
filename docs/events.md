# Events

An event is a standard `@emit` signature. The device-connect SDK builds the JSON from the arguments and broadcasts it — no schema file to author.

## Canonical events

| Event | When to emit |
|---|---|
| `accelerator.interconnect_fault` | NVLink / XGMI / PCIe link failure |
| `accelerator.ecc_uncorrectable` | uncorrectable ECC / DBE |
| `accelerator.thermal_throttle` | sustained thermal throttle |
| `accelerator.power_throttle` | sustained power-cap throttle |
| `accelerator.fatal_fault` | fatal hardware fault (Xid 79, GPU hang) |
| `accelerator.heartbeat` | periodic liveness + telemetry snapshot |

## The signature

```python
@emit("accelerator.interconnect_fault")
async def interconnect_fault(
    self,
    severity: str,             # info | degraded | critical
    confidence: float,
    topology: dict,            # link_type, local_port, peer_device_id, fabric_domain
    vendor_evidence: list,     # raw signals: [{source, code, value}]
    normalized_effect: dict,   # communication_path, bandwidth_impact, ...
    recommended_actions: list, # safe RPCs to call in response
    disallowed_actions: list,  # RPCs to refuse while this fault is active
    labels: dict,              # fault_class, fault_domain, severity tier
):
    """Interconnect fault on an intra- or inter-node link."""
```

`severity` + `recommended_actions` + `disallowed_actions` are what let an agent act safely: it reads the normalized fault, runs a recommended action, and the mesh refuses anything in `disallowed_actions`. `vendor_evidence` keeps the raw Xid / replay counts for forensics without leaking them into consumer logic.

## What the SDK emits

Calling `interconnect_fault(severity="degraded", ...)` broadcasts:

```json
{
  "event_type": "accelerator.interconnect_fault",
  "severity":   "degraded",
  "confidence": 0.92,
  "device":   { "vendor": "nvidia", "model": "H100", "device_id": "gpu-042" },
  "topology": { "link_type": "nvlink", "local_port": "nvlink3",
                "peer_device_id": "gpu-043", "fabric_domain": "rack12-nvsw02" },
  "vendor_evidence": [
    { "source": "dcgm",       "code": "NVLINK_REPLAY_ERRORS", "value": 18492 },
    { "source": "nvidia-xid", "code": "XID_74" }
  ],
  "normalized_effect": { "communication_path": "degraded", "bandwidth_impact": "probable" },
  "recommended_actions": ["run_link_diagnostic", "drain_device"],
  "disallowed_actions":  ["reset_link", "isolate"],
  "labels": { "fault_class": "interconnect", "fault_domain": "link", "severity": "degraded" }
}
```

You author the signature, not this JSON. The SDK adds `event_id` and `ts` automatically.
