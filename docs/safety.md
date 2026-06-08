# Safety Model

Polyglot encodes safety at the contract level. Drivers MUST honor these semantics.

## `recommended_actions` and `disallowed_actions`

- `recommended_actions` is the **driver-vetted** list of RPCs the driver considers safe in response to this event. It MUST be a subset of the driver's exposed RPCs.
- `disallowed_actions` is the **driver-vetted** list of RPCs the driver explicitly forbids in response to this event. The fleet service MUST refuse to invoke RPCs in `disallowed_actions` while the event is active, even if the caller has permission generally.
- These lists are situational. The same RPC MAY appear in `recommended_actions` for one event and `disallowed_actions` for another.

!!! example "Example"
    On an `accelerator.interconnect_fault` with `severity: degraded`, a driver might publish:

    ```json
    "recommended_actions": ["run_link_diagnostic", "drain_device"],
    "disallowed_actions":  ["reset_link_without_drain", "estop"]
    ```

    An agent observing this event can invoke `drain_device` safely. The fleet service will refuse `estop` on this device for as long as the event is active — even if the agent's general permissions would allow `estop`.

## Confirmation tokens

RPCs with `requires_confirmation: true` MUST refuse invocation without a fleet-service-issued confirmation token. The token mechanism is defined in `mhp-core`. Drivers MUST:

1. Validate the token's signature against the fleet service's published key.
2. Validate the token's scope — it MUST be scoped to *this device* and *this RPC*.
3. Validate the token's expiration.

Calling without a valid token MUST return `accelerator.error.requires_confirmation`.

## Estop

The `estop=True` annotation is an MHP-level promise:

- The RPC MUST be safe to invoke unilaterally without coordination with other agents.
- The RPC MUST be idempotent.
- The fleet service MAY invoke estop RPCs without consumer authorization in response to certain canonical events (defined in the schema repository per event type).

## Side-effect honesty

Drivers MUST label RPCs accurately. Labeling a destructive RPC as `side_effects: "none"` is a conformance failure caught by the test suite (see [Conformance Suite](conformance-suite.md)).

## The safety triangle

The contract enforces safety through three independent checks:

```
                    ┌─────────────────────────┐
                    │   recommended_actions   │
                    │   (driver, per event)   │
                    └───────────┬─────────────┘
                                │
                                ▼
   ┌─────────────────┐   ┌─────────────────┐   ┌──────────────────────────┐
   │  side_effects   │ + │   estop=True    │ + │  requires_confirmation   │
   │  (RPC label)    │   │  (RPC marker)   │   │  (RPC label)             │
   └─────────────────┘   └─────────────────┘   └──────────────────────────┘
```

A safe action is one where the *agent's* grant matches the RPC's `side_effects` envelope, the RPC is in the event's `recommended_actions`, and any required confirmation token is in hand. Any check failing refuses the action — the driver doesn't decide unilaterally, and the agent doesn't decide unilaterally.
