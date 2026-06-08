# Polyglot Accelerator Driver Spec

**Status:** Draft · **Contract version:** `2026-06-01`

One vendor-neutral way for agents and humans to observe and control any accelerator — NVIDIA, AMD, Trainium, TPU, custom silicon — over the [device-connect](https://github.com/arm/device-connect) mesh.

## The whole idea

An accelerator driver is a device-connect driver that declares a **standard set of `@emit` and `@rpc` signatures**. The SDK does the rest: it builds the JSON payloads from your method arguments, generates the parameter schemas, and broadcasts the manifest on the mesh.

There is nothing to author beyond the standard signatures. A consumer — a dashboard, or an SRE agent over MCP — keys on the canonical event and RPC names, never on vendor.

## Standardized vs. vendor-owned

| Standardized (this spec) | Vendor-owned |
|---|---|
| event names + their fields (`@emit` signatures) | how you read NVML / ROCm-SMI / Neuron |
| RPC names + their labels (`@rpc` signatures) | thresholds, Xid policy, severity calculus |

The spec fixes the vocabulary. The vendor owns the judgment behind it.

## Identity

Every driver sets `device_type = "accelerator"` and declares `vendor`, `model`, `device_id`, `host_id`. That's the manifest the mesh broadcasts — nothing else required.

## Read next

- **[Events](events.md)** — the `@emit` signatures.
- **[RPCs](rpcs.md)** — the `@rpc` signatures.
- **[Reference Driver](driver.md)** — both, end to end.
