# Getting Started

A practical checklist for shipping a conformant driver.

## 1. Install the contract

```bash
pip install polyglot-accelerator
```

That one package is the entire contract: the base class, the typed payloads, the label enums, and the conformance suite.

## 2. Read the contract

- [Overview](overview.md) — what Polyglot is and isn't.
- [Identity Manifest](manifest.md), [Required Events](events.md), [Required RPCs](rpcs.md). These three sections are 80% of conformance.

## 3. Start from the reference skeleton

- Subclass `AcceleratorDriverBase` from the [Reference Skeleton](skeleton.md).
- Set `VENDOR`. Implement the private `_*` hooks against your SDK.

## 4. Wire up the conformance suite

- The suite ships inside the package — run `python -m polyglot_accelerator.conformance` against your driver.
- Add a CI job to your driver's repo that runs the suite on every PR.
- Embed the conformance badge in your driver's README so consumers can see the level at a glance.

## 5. Publish

- Publish your driver as `polyglot-accelerator-driver-<vendor>` to PyPI.
- Link to the conformance badge and the live conformance report.

## 6. Join the working group

- Subscribe to the WG mailing list / Slack channel (linked from the repo).
- Propose your vendor's contributions to the next dated release as RFCs.
- Participate in reviewing other vendors' RFCs — that's how we maintain cross-vendor implementability as a hard gate.

## Common questions

??? question "Do I have to implement every RECOMMENDED RPC to ship?"
    No. `core` is the floor for production use. `extended` is aspirational. Many vendors will ship `core` first and grow into `extended` over a few releases.

??? question "What if my hardware genuinely doesn't have one of the REQUIRED events (e.g. no NVLink-equivalent)?"
    Don't emit it. The conformance suite checks the *shape* of every event you *do* emit; it doesn't require you to manufacture events for hardware features you don't have. A device with no intra-node fabric simply never emits an interconnect fault for that fabric.

??? question "Can I add my own event types?"
    Under a vendor prefix, yes (`nvidia.power_anomaly`). These are non-canonical and consumer code won't depend on them. To add a canonical event type, file an RFC.

??? question "How do I handle hardware that supports a small subset of the canonical RPCs (e.g. a low-end inference accelerator with no `isolate` capability)?"
    Either ship `experimental` (which is allowed to be partial), or stub the missing RPC to return `accelerator.error.not_supported`. Consumers will see the gap via the conformance level. The deeper fix is to file an RFC introducing a capability tier below `core` for this class of hardware.

??? question "Who decides what's `severity: critical` vs `degraded` for my hardware?"
    You do, in the driver. The schema reviews mappings, not implementations. The WG conversation is "is your mapping defensible to other vendors and consumers?" — not "is your threshold right?"

## Welcome to the fleet

Once your driver lands `conformance_level: core` and shows up on the mesh, an Anthropic SRE handler written against `accelerator.interconnect_fault` works on your hardware on day one — no per-vendor code path on their side, no per-customer onboarding on yours. That's the deal.
