# Identity Manifest

Every driver MUST register an identity manifest at startup. The manifest is queryable via `fleet.discover()` and is the source of truth for all labels the fleet service applies to events from that device.

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
| `schema_versions` | array of strings | All Polyglot schema versions this driver can emit. MUST contain at least one stable version. |

## Required topology block

```json
"topology": {
  "intra_node_fabric": "nvlink_v4" | "xgmi" | "neuronlink" | "ici" | "none",
  "intra_node_peers":  ["gpu-041", "gpu-043", ...],
  "fabric_domain":     "rack12-nvsw02",
  "inter_node_fabric": "infiniband_ndr" | "roce_v2" | "efa" | "ocs" | "none",
  "pci_address":       "0000:1a:00.0"
}
```

The topology block is REQUIRED. Drivers that genuinely cannot determine some fields (e.g. a development board with no fabric) MUST emit `null` rather than omit the field. The fleet service uses topology to compute blast-radius queries:

```python
fleet.discover("fabric_domain=rack12-nvsw02 severity=critical")
```

## Optional fields

`tenant`, `labels.<vendor>.*`, `hw_revision`, `serial`, `power_cap_w`, `mem_total_gb`. Drivers MAY add these but consumer code MUST NOT depend on their presence.

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
  "topology": {
    "intra_node_fabric": "nvlink_v4",
    "intra_node_peers":  ["gpu-040", "gpu-041", "gpu-043"],
    "fabric_domain":     "rack12-nvsw02",
    "inter_node_fabric": "infiniband_ndr",
    "pci_address":       "0000:1a:00.0"
  },
  "tenant": "training-prod"
}
```
