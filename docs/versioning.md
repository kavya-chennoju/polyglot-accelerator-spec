# Schema Versioning

The contract is the `polyglot-accelerator` package. "Schema version" is that package's version. Versioning the contract means versioning the package — there is no separate schema artifact to version independently.

## Declaration

Drivers MUST declare the contract versions they support in `identity.schema_versions`. Drivers SHOULD support at least two consecutive stable versions during a transition window.

## Emission

Every emitted event MUST carry `schema_version` — the `polyglot-accelerator` version the payload was built against:

```json
{ "schema_version": "2026-06-01" }
```

## Negotiation

The fleet service negotiates a per-consumer contract version. Drivers MUST NOT emit events at a version no consumer has subscribed to. Drivers SHOULD emit at the highest stable version they support unless a downgrade was negotiated.

## Compatibility rules

| Change type | Rule |
|---|---|
| **Additive** — new optional field, new enum value, new event type, new label | Minor release of the package (same dated version, `+1` suffix). Drivers and consumers MUST accept unknown additive fields gracefully. |
| **Breaking** — rename, remove, change semantics | New dated version (e.g. `2026-12-01`). Both versions MUST be supported in parallel for at least 6 months (deprecation window). The deprecated version MUST be labelled `stability: deprecated` during that window. |

Drivers MUST NOT mix contract versions within a single event payload.

## Why date-stamped versions?

Date stamps make deprecation timelines unambiguous and human-readable. `2026-06-01` deprecated in favor of `2026-12-01` carries its own timeline. Semver-style versions (`v2.3.1`) hide the schedule and require an external changelog to interpret.

## How the contract ships

One package, one dependency:

```
polyglot-accelerator/           # the contract — pip install polyglot-accelerator
├── base.py                     # AcceleratorDriverBase
├── payloads.py                 # InterconnectFault, EccUncorrectable, ThermalThrottle, ...
├── labels.py                   # FaultClass, FaultDomain, Stability, SideEffects, ... (enums)
├── rpcs.py                     # canonical RPC names + signatures
└── conformance/                # the conformance suite
```

Vendors pin a version (`polyglot-accelerator==2026.6.1`), subclass `AcceleratorDriverBase`, and import the payload types and label enums. Upgrading the contract is a dependency bump; the compatibility rules above govern what breaks.

!!! note "No language bindings to generate"
    Because every driver and consumer is Python, the typed classes in this package are consumed directly — there's nothing to generate, export, or keep in sync across languages. If a non-Python consumer ever appears, JSON Schema can be *generated from* these typed classes at that point. Until then, the package is the whole story.
