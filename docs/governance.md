# Governance

Schema changes follow the RFC process documented in [`polyglot-accelerator-schema/RFCs/`](https://github.com/kavya-chennoju/polyglot-accelerator-spec). RFCs are accepted on the merits of:

- **A canonical use case** — multiple consumers want the field, event, or RPC.
- **Cross-vendor implementability** — NVIDIA and at least one non-NVIDIA vendor have a path to support.
- **A migration plan** — additive or dated breaking change with deprecation window.

Vendor-specific data should never need an RFC; it lives in [`vendor_evidence[]`](extensions.md) or [`labels.<vendor>.*`](labels.md).

## RFC lifecycle

```
Draft  →  Public review  →  Working-group vote  →  Accepted  →  In schema
                                                       │
                                                       └─ Rejected (with rationale)
```

Each RFC is a markdown file in the schema repository's `RFCs/` directory. Drafts are open PRs; accepted RFCs are merged and reflected in the next dated schema version.

## Working group

Polyglot follows the [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/) governance model:

- **Vendor-open** — any silicon vendor can join. Currently expected: NVIDIA, AMD, Intel/Habana, AWS Neuron, Google TPU, Meta MTIA.
- **Consumer-open** — fleet operators (Anthropic, hyperscalers, research labs) participate as canonical consumers.
- **RFC-driven** — all changes flow through public RFCs. No unilateral vendor extensions to canonical surface.
- **Stability tiers** — every event type and RPC carries a `stability` label: `experimental` / `stable` / `deprecated`. Promotion between tiers requires WG sign-off.
- **Cadence** — dated schema versions (`2026-06-01`, `2026-12-01`, …) ship on a 6-month cycle. Additive minor revisions can land between dates.

## What gets reviewed

The schema reviews **mappings**, not implementations.

- "NVIDIA's `XID_74` maps to `accelerator.interconnect_fault` at severity `degraded` when replay errors > 1000/60s" — *that* gets reviewed in the WG.
- "NVIDIA's driver implements that mapping by calling NVML's `nvmlDeviceGetNvLinkErrorCounter`" — *that* stays in NVIDIA's repository.

This split is the deal: vendors own implementations, the WG owns semantic equivalence.

## Stability tiers

| Tier | Meaning | Consumer behavior |
|---|---|---|
| `experimental` | Newly introduced; may change in minor revisions. | Opt-in via explicit subscription. |
| `stable` | Frozen semantics within a major schema version. Backward-compatible additive changes allowed. | Default subscription tier. |
| `deprecated` | Marked for removal in a future dated version. Continues to function for the deprecation window. | Surfaced in dashboards for migration planning. |

## How vendors contribute

1. Open a draft RFC in `polyglot-accelerator-schema/RFCs/` describing the proposed change.
2. Reference at least one cross-vendor consumer that would benefit.
3. Update the conformance suite to exercise the new behavior.
4. WG public review (minimum 14 days).
5. WG sign-off; RFC merged; reflected in next dated schema version.

The schema repository ships with a contribution guide and an RFC template to make this concrete for first-time contributors.
