# Extension Points

Vendors will always have signals, fields, and RPCs that aren't in the canonical surface. Polyglot provides three controlled extension points so per-vendor specifics don't leak into consumer logic.

## `vendor_evidence[]`

This is the *only* place raw vendor signals belong on a canonical event. Each entry:

```json
{
  "source":    "dcgm" | "nvidia-xid" | "rocm-smi" | "amd-smi"
             | "neuron-cli" | "hl-smi" | "pci-aer" | "<source>",
  "code":      "string",        // vendor-specific code
  "value":     0,               // when meaningful (or null)
  "threshold": 0,               // when meaningful (or null)
  "message":   "string or null" // vendor-supplied message
}
```

Consumers SHOULD treat `vendor_evidence` as forensic data and SHOULD NOT key on it in portable logic. Tooling MAY surface `vendor_evidence` to humans in post-mortems and dashboards.

!!! note "Why preserve raw evidence at all?"
    The canonical event abstracts what the consumer needs. The raw signals are what the SRE needs at 3am during a post-mortem. The schema serves both — abstraction for portable code, preservation for forensics.

## Vendor-namespaced labels

Drivers MAY add vendor-specific labels under a namespaced prefix:

```json
"labels": {
  "fault_class":    "interconnect",
  "stability":      "stable",
  "evidence_grade": "direct",
  "fault_domain":   "link",
  "nvidia": {
    "persistence_mode":   "off",
    "nvswitch_partition": "p3"
  }
}
```

Consumer code MUST NOT key on `labels.<vendor>.*` in portable logic. These exist for diagnostic dashboards and vendor-internal tooling.

## Vendor-namespaced RPCs

Drivers MAY expose RPCs outside the canonical set under a namespaced prefix:

```python
@rpc("nvidia.dump_nvswitch_state",
     labels={"category": "diagnostic", "side_effects": "none",
             "stability": "experimental", "idempotent": True,
             "requires_confirmation": False})
async def dump_nvswitch_state(self): ...
```

These do NOT count toward conformance and consumer code MUST NOT depend on their presence. They exist for vendor-internal tooling and forensic deep dives.

## The extension contract

The rule is the same across all three extension points: **vendor-specific data is allowed, but it lives in a designated bucket where consumers know not to depend on it.** That preserves the abstraction for portable code while letting vendors ship the full depth of their telemetry.

A driver that smuggles vendor specifics onto top-level canonical fields (e.g. adding `nvlink_replay_errors` directly under the event root instead of inside `vendor_evidence[]`) is a conformance failure caught by the test suite.
