# Governance

Contract changes follow an RFC process in the [`polyglot-accelerator`](https://github.com/kavya-chennoju/polyglot-accelerator-spec) repository. An RFC is a proposed change to the package — a new event type, a new field on a payload, a new label enum value, a new RPC. RFCs are accepted on the merits of:

- **A canonical use case** — multiple consumers want the field, event, or RPC.
- **Cross-vendor implementability** — NVIDIA and at least one non-NVIDIA vendor have a path to support.
- **A migration plan** — additive or dated breaking change with deprecation window.

Vendor-specific data should never need an RFC; it lives in [`vendor_evidence[]`](extensions.md) or [`labels.<vendor>.*`](labels.md).

## RFC lifecycle

```
Draft  →  Public review  →  Working-group vote  →  Accepted  →  Released in package
                                                       │
                                                       └─ Rejected (with rationale)
```

Each RFC is a markdown file in the repository's `RFCs/` directory. Drafts are open PRs; accepted RFCs are merged and ship in the next dated release of the `polyglot-accelerator` package.

## Working group

Polyglot follows the [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/) governance model:

- **Vendor-open** — any silicon vendor can join. Currently expected: NVIDIA, AMD, Intel/Habana, AWS Neuron, Google TPU, Meta MTIA.
- **Consumer-open** — fleet operators (Anthropic, hyperscalers, research labs) participate as canonical consumers.
- **RFC-driven** — all changes flow through public RFCs. No unilateral vendor extensions to the canonical surface.
- **Stability tiers** — every event type and RPC carries a `stability` label: `experimental` / `stable` / `deprecated`. Promotion between tiers requires WG sign-off.
- **Cadence** — dated releases (`2026-06-01`, `2026-12-01`, …) ship on a 6-month cycle. Additive minor releases land between dates.

## What gets reviewed

The contract reviews **mappings**, not implementations.

- "NVIDIA's `XID_74` maps to `accelerator.interconnect_fault` at severity `degraded` when replay errors > 1000/60s" — *that* gets reviewed in the WG.
- "NVIDIA's driver implements that mapping by calling NVML's `nvmlDeviceGetNvLinkErrorCounter`" — *that* stays in NVIDIA's repository.

This split is the deal: vendors own implementations, the WG owns semantic equivalence — expressed as the typed payloads and label enums in the shared package.

## Stability tiers

| Tier | Meaning | Consumer behavior |
|---|---|---|
| `experimental` | Newly introduced; may change in minor releases. | Opt-in via explicit subscription. |
| `stable` | Frozen semantics within a major (dated) version. Backward-compatible additive changes allowed. | Default subscription tier. |
| `deprecated` | Marked for removal in a future dated version. Continues to function for the deprecation window. | Surfaced in dashboards for migration planning. |

## How vendors contribute

1. Open a draft RFC in `polyglot-accelerator/RFCs/` describing the proposed change.
2. Reference at least one cross-vendor consumer that would benefit.
3. Update the conformance suite to exercise the new behavior.
4. WG public review (minimum 14 days).
5. WG sign-off; RFC merged; ships in the next dated release.

The repository ships with a contribution guide and an RFC template to make this concrete for first-time contributors.
