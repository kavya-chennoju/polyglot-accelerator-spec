# Overview

This is the conformance specification for **accelerator-class drivers** that participate in a Polyglot fleet. It defines the contract every driver MUST satisfy in order to be recognized as a valid accelerator by the fleet service and operated by vendor-neutral consumer code — humans, dashboards, and SRE agents over MCP.

This document does **not** specify driver internals. How you scrape NVML / DCGM / ROCm-SMI / Neuron / hl-smi is your business. It specifies:

- what your driver MUST emit (canonical typed event payloads),
- what RPCs it MUST expose (vendor-neutral action names with declared semantics),
- what labels it MUST attach (for routing, RBAC, discovery),
- how it MUST evolve (versioning + deprecation).

## The contract lives in one package

Every driver depends on a single package — **`polyglot-accelerator`** — and that package *is* the contract:

| The package exports | Which means |
|---|---|
| `AcceleratorDriverBase` | You subclass it. It enforces the contract; you supply vendor behavior. |
| Typed payloads (`InterconnectFault`, …) | The canonical event structure. Constructing one is how you conform. |
| Label enums (`FaultClass`, `SideEffects`, …) | The governed vocabulary. You can't emit a value that isn't in the enum. |
| RPC name + signature constants | The vendor-neutral action surface. |

```python
pip install polyglot-accelerator
```

There is no separate schema file, no parallel JSON artifact, no second source of truth. The typed classes are the schema; the package version is the schema version.

## Why a shared contract and not just self-describing drivers?

A self-describing driver gives syntactic discovery — *what* events it emits and *what* RPCs it exposes — but not semantic equivalence. Two drivers can both advertise `accelerator.interconnect_fault` while disagreeing about what `severity:degraded` *means* and which actions are safe in response. Consumer code is back to per-vendor branching the moment vendor A and vendor B disagree.

The shared package is the negotiated common ground. Because NVIDIA's driver and AMD's driver import the **same** `InterconnectFault` type and the **same** `Severity` enum, they cannot disagree about structure or vocabulary. The only thing left to each vendor is the mapping — *which* raw signal becomes *which* canonical event at *which* severity — and that's exactly the per-vendor judgment we want to keep vendor-side.

!!! info "Analogy"
    A shared protobuf / typed-client library does this for RPC systems: everyone imports the same generated types, so nobody argues about wire structure — they only implement behavior. `polyglot-accelerator` is that shared library for accelerator telemetry and control.

## Document conventions

- **RFC 2119 vocabulary** — `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY` carry their standard meanings.
- **Canonical names** — event types, RPC names, label keys, and enum values appear in `code style` and are case-sensitive. The authoritative definitions are the exported types in the `polyglot-accelerator` package.
- **`schema_version`** — the version of the `polyglot-accelerator` contract package a driver emits against (e.g. `2026-06-01`).

## What success looks like

A `core`-conformant driver passes every test in the conformance suite and can be deployed into a heterogeneous fleet alongside drivers from other vendors with no consumer-side changes. An Anthropic SRE handler that worked for NVIDIA H100s yesterday works for AMD MI300X today — and works for Trainium 3 next quarter — because every driver imports the same contract package.
