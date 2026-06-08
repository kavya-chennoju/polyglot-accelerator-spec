# Overview

This is the conformance specification for **accelerator-class drivers** that participate in a Polyglot fleet. It defines the contract every driver MUST satisfy in order to be recognized as a valid accelerator by the fleet service and operated by vendor-neutral consumer code — humans, dashboards, and SRE agents over MCP.

This document does **not** specify driver internals. How you scrape NVML / DCGM / ROCm-SMI / Neuron / hl-smi is your business. It specifies:

- what your driver MUST emit (canonical event payloads),
- what RPCs it MUST expose (vendor-neutral action names with declared semantics),
- what labels it MUST attach (for routing, RBAC, discovery),
- how it MUST evolve (schema versioning + deprecation).

## Why a contract and not just self-describing drivers?

A self-describing driver gives syntactic discovery — *what* events it emits and *what* RPCs it exposes — but not semantic equivalence. Two drivers can both advertise `accelerator.interconnect_fault` while disagreeing about what `severity:degraded` *means* and which actions are safe in response. Consumer code is back to per-vendor branching the moment vendor A and vendor B disagree.

The published contract is the negotiated common ground. Drivers conform to it; consumers code against it; an SRE agent operates the whole fleet without knowing which vendor's silicon backs which device.

!!! info "Analogy"
    TCP/IP didn't ask each vendor to define what "packet" means. The IETF published RFCs; vendors implemented to the RFCs. That's why a Mac talks to a Cisco router talks to a Linux server. Polyglot plays the same role for accelerator telemetry and control.

## Document conventions

- **RFC 2119 vocabulary** — `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY` carry their standard meanings.
- **Canonical names** — event types, RPC names, label keys, and enum values appear in `code style` and are case-sensitive.
- **Versioned URIs** — schema URIs include the dated schema version (`/2026-06-01/`).
- **JSON examples** — illustrative; the authoritative shapes are the JSON Schema files in the schema repository.

## What success looks like

A `core`-conformant driver passes every test in the conformance suite and can be deployed into a heterogeneous fleet alongside drivers from other vendors with no consumer-side changes. An Anthropic SRE handler that worked for NVIDIA H100s yesterday works for AMD MI300X today — and works for Trainium 3 next quarter — because the contract is the abstraction.
