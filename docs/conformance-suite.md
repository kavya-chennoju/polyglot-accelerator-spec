# Conformance Suite

The conformance test suite (`polyglot-accelerator-conformance`) is published in the schema repository. A driver MUST pass the entire `core` suite to advertise `conformance_level: "core"`. The suite is run automatically against every contributor's PR in CI and provides a public conformance badge.

## What the suite exercises

1. **Manifest validation** — every REQUIRED field present, every value within enum bounds.
2. **Event schema validation** — every event the driver emits validates against the JSON Schema for its declared `schema_version`.
3. **Label completeness** — every event and RPC carries every REQUIRED label.
4. **RPC contract** — every REQUIRED RPC is present, returns schema-conformant payloads, validates inputs and outputs.
5. **Idempotence** — repeated invocation of idempotent RPCs returns identical state.
6. **Confirmation tokens** — RPCs marked `requires_confirmation: true` refuse invocation without a valid token.
7. **Side-effect honesty** — RPCs labelled `side_effects: "none"` are verified non-destructive via probe RPCs before and after.
8. **Recommended/disallowed action consistency** — the fleet service is fed synthetic events; verified the driver refuses RPCs in `disallowed_actions`.
9. **Schema version negotiation** — driver respects subscriber-negotiated versions.
10. **Heartbeat liveness** — heartbeat arrives within the 30 s window; stops within 60 s of `drain_device`; resumes within 60 s of `cancel_drain`.

## Running the suite locally

```bash
pip install polyglot-accelerator-conformance

# Point the suite at a running driver instance.
polyglot-conformance run \
  --driver-host  localhost \
  --driver-port  5500      \
  --schema-version 2026-06-01 \
  --suite        core
```

Output:

```
manifest_validation              ✓
event_schema_validation          ✓
label_completeness               ✓
rpc_contract                     ✓
idempotence                      ✓
confirmation_tokens              ✓
side_effect_honesty              ✓
recommended_disallowed_actions   ✓
schema_version_negotiation       ✓
heartbeat_liveness               ✓

10 / 10 passed.  Driver is conformant: core (2026-06-01).
```

## Conformance badge

Conformant drivers get a public badge embedded in their README:

```markdown
![Polyglot Conformance](https://schemas.polyglot.org/badge/<driver>/core/2026-06-01.svg)
```

The badge tracks the most recent CI run against the published schema and downgrades automatically if a schema-version bump introduces incompatibilities.

## Failing conformance

A failing test produces a structured report citing the exact schema rule violated and the offending payload, so the driver author can fix without spelunking. Example:

```
✗ label_completeness

  Event #4 emitted by gpu-042 missing REQUIRED label `evidence_grade`.

  Spec:      polyglot-accelerator-spec / labels (§6.1)
  Schema:    https://schemas.polyglot.org/accelerator/2026-06-01/labels/emit.json
  Payload:   { "event_type": "accelerator.interconnect_fault", "labels": {
               "fault_class":  "interconnect",
               "fault_domain": "link",
               "stability":    "stable"
               // evidence_grade missing ← required
             } }
```
