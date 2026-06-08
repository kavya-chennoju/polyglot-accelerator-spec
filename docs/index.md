# Polyglot Accelerator Driver Specification

**Schema version:** `2026-06-01`
**Status:** Draft
**Audience:** Authors of accelerator drivers — NVIDIA, AMD, Intel/Habana, AWS Neuron, Google TPU, Meta MTIA, custom silicon.

---

A vendor-neutral observability and control contract for heterogeneous accelerator fleets. One canonical event vocabulary, one set of RPC names, one safety model — across every vendor's silicon. Vendor specifics stay inside the driver; consumer code (humans, dashboards, SRE agents over MCP) never branches on vendor.

## The contract is one package

The entire contract ships as a single Python package: **`polyglot-accelerator`**. It exports three things:

- **`AcceleratorDriverBase`** — the base class every driver subclasses.
- **Typed event payloads** — `InterconnectFault`, `EccUncorrectable`, `ThermalThrottle`, … . These *are* the schema. Constructing one guarantees the structure.
- **Label enums** — `FaultClass`, `SideEffects`, `Stability`, … . The governed vocabulary.

Every vendor runs `pip install polyglot-accelerator`, subclasses `AcceleratorDriverBase`, and populates the typed payloads. That's the whole contract — no separate schema file to fetch, no second source of truth to keep in sync.

!!! tip "Why a package and not a separate JSON Schema?"
    The driver's decorators (`@emit`, `@rpc`) plus the shared typed payloads already declare the structure, the event names, and the labels — and MHP broadcasts all of it on the mesh. A separate JSON Schema artifact would just duplicate what the typed classes already express. The package **is** the schema.

## Quick orientation

!!! note "Start here if you are…"
    - **A vendor driver author** → [Overview](overview.md) → [Identity Manifest](manifest.md) → [Required Events](events.md) → [Required RPCs](rpcs.md) → [Reference Skeleton](skeleton.md).
    - **A consumer (SRE handler / agent integration)** → [Required Events](events.md) → [Safety Model](safety.md) → [Labels](labels.md).
    - **Reviewing the proposal** → [Overview](overview.md) → [Governance](governance.md) → [Conformance Suite](conformance-suite.md).

## What Polyglot standardizes

| Standardized (in the `polyglot-accelerator` package) | **Not** standardized (vendor-owned) |
|---|---|
| Typed event payloads — the canonical structure and fields | Driver implementation — how NVML / DCGM / ROCm-SMI gets scraped |
| Vendor-neutral RPC names and semantics (`run_link_diagnostic`, `drain_device`, `isolate`) | Per-vendor judgment — thresholds, Xid policies, severity calculus |
| Label vocabulary for routing, RBAC, and discovery | Raw vendor telemetry sources (these stay as the vendor ships them) |
| The driver base class and capability surface | Transport / discovery / registry / security (those are MHP's job) |

## Companion artifacts

- **`polyglot-accelerator`** — the contract: base class, typed payloads, label enums, conformance suite. The one dependency every driver shares.
- **`mhp-core`** — the underlying transport / discovery / security / estop protocol.

---

*Polyglot is part of the broader Model Hardware Protocol (MHP) ecosystem — a vendor-neutral fabric for AI agents to safely discover and operate physical devices.*
