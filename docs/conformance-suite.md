# Conformance Suite

The conformance suite ships **inside the `polyglot-accelerator` package** (`polyglot_accelerator.conformance`). A driver MUST pass the entire `core` suite to advertise `conformance_level: "core"`. The suite is run automatically against every contributor's PR in CI and provides a public conformance badge.

## What the suite exercises

1. **Manifest validation** — every REQUIRED identity field present, every value within enum bounds.
2. **Event type validation** — every event the driver emits is a valid `polyglot-accelerator` payload type, fully populated.
3. **Label completeness** — every event and RPC carries every REQUIRED label, with values drawn from the package's label enums.
4. **RPC contract** — every REQUIRED RPC is present, accepts the declared signature, returns a conformant typed result.
5. **Idempotence** — repeated invocation of idempotent RPCs returns identical state.
6. **Confirmation tokens** — RPCs marked `requires_confirmation: true` refuse invocation without a valid token.
7. **Side-effect honesty** — RPCs labelled `side_effects: "none"` are verified non-destructive via probe RPCs before and after.
8. **Recommended/disallowed action consistency** — the fleet service is fed synthetic events; verified the driver refuses RPCs in `disallowed_actions`.
9. **Version negotiation** — driver respects subscriber-negotiated contract versions.
10. **Heartbeat liveness** — heartbeat arrives within the 30s window; stops within 60s of `drain_device`; resumes within 60s of `cancel_drain`.

## Running the suite locally

```bash
pip install polyglot-accelerator

# Point the suite at a running driver instance.
python -m polyglot_accelerator.conformance \
  --driver-host localhost \
  --driver-port 5500      \
  --suite       core
```

Output:

```
manifest_validation              ✓
event_type_validation            ✓
label_completeness               ✓
rpc_contract                     ✓
idempotence                      ✓
confirmation_tokens              ✓
side_effect_honesty              ✓
recommended_disallowed_actions   ✓
version_negotiation              ✓
heartbeat_liveness               ✓

10 / 10 passed.  Driver is conformant: core (2026-06-01).
```

## Conformance badge

Conformant drivers get a public badge in their README, tracking the most recent CI run against the pinned contract version. The badge downgrades automatically if a contract bump introduces incompatibilities.

## Failing conformance

A failing test cites the exact contract rule violated and the offending payload, so the driver author can fix without spelunking:

```
✗ label_completeness

  Event #4 emitted by gpu-042 missing REQUIRED label `evidence_grade`.

  Spec:     polyglot-accelerator-spec / labels
  Type:     polyglot_accelerator.InterconnectFault
  Payload:  labels = {
              "fault_class":  "interconnect",
              "fault_domain": "link",
              "stability":    "stable"
              // evidence_grade missing ← required
            }
```

Because the payloads are typed, most structural mistakes are caught at construction time in the driver itself — the suite catches the semantic and behavioral rules the type system can't (label completeness against the spec, side-effect honesty, idempotence, confirmation-token enforcement).
