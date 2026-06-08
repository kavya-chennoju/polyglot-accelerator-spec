# Polyglot Accelerator Driver Specification

**Schema version:** `2026-06-01`
**Status:** Draft
**Audience:** Authors of accelerator drivers — NVIDIA, AMD, Intel/Habana, AWS Neuron, Google TPU, Meta MTIA, custom silicon.

---

A vendor-neutral observability and control contract for heterogeneous accelerator fleets. One canonical event vocabulary, one set of RPC names, one safety model — across every vendor's silicon. Vendor specifics stay inside the driver; consumer code (humans, dashboards, SRE agents over MCP) never branches on vendor.

This specification defines the contract every driver MUST satisfy to participate in a Polyglot fleet. It does **not** specify driver internals — how you scrape NVML, DCGM, ROCm-SMI, Neuron SDK, or hl-smi is your business. It specifies what your driver MUST emit, what RPCs it MUST expose, what labels it MUST attach, and how it MUST evolve.

[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) vocabulary (MUST / SHOULD / MAY) applies throughout.

## Quick orientation

!!! tip "Start here if you are…"
    - **A vendor driver author** → [Overview](overview.md) → [Identity Manifest](manifest.md) → [Required Events](events.md) → [Required RPCs](rpcs.md) → [Reference Skeleton](skeleton.md).
    - **A consumer (SRE handler / agent integration)** → [Required Events](events.md) → [Safety Model](safety.md) → [Labels](labels.md).
    - **Reviewing the proposal** → [Overview](overview.md) → [Governance](governance.md) → [Conformance Suite](conformance-suite.md).

## The contract at a glance

| What Polyglot standardizes | What Polyglot does **not** standardize |
|---|---|
| Canonical event payload schema (severity, topology, evidence, recommended_actions, …) | Driver implementation — how NVML / DCGM / ROCm-SMI gets scraped |
| Vendor-neutral RPC names and semantics (`run_link_diagnostic`, `drain_device`, `isolate`) | Per-vendor judgment — thresholds, Xid policies, severity calculus |
| Label vocabulary for routing, RBAC, and discovery | Raw vendor telemetry sources (these stay as the vendor ships them) |
| Driver capability declaration (what a valid accelerator driver must expose) | Transport / discovery / registry / security (those are MHP's job) |

## Companion artifacts

- [`polyglot-accelerator-schema`](https://github.com/kavya-chennoju/polyglot-accelerator-spec) — JSON Schema files, language bindings, conformance suite.
- `mhp-core` — the underlying transport / discovery / security / estop protocol.

---

*Polyglot is part of the broader Model Hardware Protocol (MHP) ecosystem — a vendor-neutral fabric for AI agents to safely discover and operate physical devices.*
