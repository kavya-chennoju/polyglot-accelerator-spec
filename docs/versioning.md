# Schema Versioning

## Declaration

Drivers MUST declare all schema versions they support in `identity.schema_versions`. Drivers SHOULD support at least two consecutive stable versions during a transition window.

## Emission

Every emitted event MUST carry `schema_version` and `schema_uri`. The version MUST be one the driver declared.

```json
{
  "schema_version": "2026-06-01",
  "schema_uri":     "https://schemas.polyglot.org/accelerator/2026-06-01/interconnect_fault.json"
}
```

## Negotiation

The fleet service negotiates a per-consumer schema version. Drivers MUST NOT emit events at a schema version no consumer has subscribed to. Drivers SHOULD emit at the highest stable version they support unless a downgrade was negotiated.

## Compatibility rules

| Change type | Rule |
|---|---|
| **Additive** — new optional field, new enum value, new event type, new label | Minor revision; same dated version with a `+1` suffix. Drivers and consumers MUST accept unknown additive fields gracefully. |
| **Breaking** — rename, remove, change semantics | New dated schema version. Both versions MUST be supported in parallel for at least 6 months (deprecation window). The deprecated version MUST be labelled `stability: deprecated` during that window. |

Drivers MUST NOT mix schema versions within a single event payload.

## Why date-stamped versions?

Date stamps make deprecation timelines unambiguous and human-readable. `2026-06-01` deprecated in favor of `2026-12-01` carries its own timeline. Semver-style versions (`v2.3.1`) hide the schedule and require an external changelog to interpret. Polyglot uses date-stamping to keep the wire payload self-describing about its lifecycle.

## Where schemas live

```
github.com/<org>/polyglot-accelerator-schema
├── events/
│   └── accelerator/
│       ├── interconnect_fault.v2026-06-01.json
│       ├── ecc_uncorrectable.v2026-06-01.json
│       └── sdc_suspected.v2026-06-01.json
├── rpcs/
│   └── accelerator/
│       ├── run_link_diagnostic.v2026-06-01.json
│       ├── drain_device.v2026-06-01.json
│       └── isolate.v2026-06-01.json
└── bindings/
    ├── python/  ← published to PyPI as polyglot-schema
    ├── go/      ← published as go module
    └── rust/    ← published to crates.io
```

Built artifacts ship as language-specific packages so drivers and consumers `import` typed structs and validate before / after the wire — they don't hand-roll dicts.
