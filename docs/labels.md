# Labels

Labels are part of the canonical contract. Drivers MUST attach them; consumers depend on them for routing, RBAC, and discovery.

## Required labels on every `@emit`

| Label | Values | Notes |
|---|---|---|
| `fault_class` | `interconnect` / `memory` / `compute` / `thermal` / `firmware` / `lifecycle` | One per event. |
| `fault_domain` | `device` / `link` / `host` / `rack` / `fabric` | Scope / blast radius. |
| `stability` | `experimental` / `stable` / `deprecated` | Propagates the event's schema stability tier. |
| `evidence_grade` | `direct` / `inferred` / `heuristic` | How the driver derived the classification. |

## Required labels on every `@rpc`

| Label | Values | Notes |
|---|---|---|
| `category` | `diagnostic` / `remediation` / `query` / `lifecycle` | One per RPC. |
| `side_effects` | `none` / `drains` / `destructive` / `state_change` | Blast-radius envelope. |
| `stability` | `experimental` / `stable` / `deprecated` | Schema stability. |
| `idempotent` | `bool` | Whether retries are safe. |
| `requires_confirmation` | `bool` | Whether autonomous invocation requires a confirmation token. |

## What labels unlock

Labels turn driver-declared surface into something a consumer can query and govern *by intent, not by name*.

```python
# Subscribe to all interconnect faults — across event types, vendors, future schema additions.
fleet.subscribe(
    "emit.labels.fault_class=interconnect severity in (degraded, critical)",
    on_link_fault,
)

# Discover every safe-to-call diagnostic RPC across the fleet.
fleet.discover("rpc.labels.category=diagnostic rpc.labels.side_effects=none")

# Agentic guardrail: an SRE agent over MCP is granted only side_effects in {none, drains}.
# It can run_link_diagnostic and drain_device, but cannot isolate / estop.
agent_grant = "rpc.labels.side_effects in (none, drains) rpc.labels.requires_confirmation=false"

# Fleet-wide audit: every destructive action and who's authorized to call it.
fleet.discover("rpc.labels.side_effects=destructive")

# Stability hygiene: only consume stable events in prod; surface experimental in staging only.
fleet.subscribe("emit.labels.stability=stable", on_event)
```

## Label enums are governed

The enum values above are the **only** permitted values — they are Python enums in the `polyglot-accelerator` package, so an invalid value won't even construct. A driver MUST NOT invent new label values (e.g. `side_effects: "mostly_harmless"`). New enum values require an RFC against the package.

## Vendor-namespaced labels

Drivers MAY add vendor-specific labels under a namespaced prefix:

```json
"labels": {
  "fault_class":     "interconnect",
  "stability":       "stable",
  "evidence_grade":  "direct",
  "fault_domain":    "link",
  "nvidia": {
    "persistence_mode":   "off",
    "nvswitch_partition": "p3"
  }
}
```

Consumer code MUST NOT key on `labels.<vendor>.*` in portable logic; these are diagnostic-only.

## Three structural things labels enable

1. **RBAC and agent guardrails live at the label boundary, not in hard-coded RPC lists.** When a new vendor ships a driver with a new RPC, the agent's permission envelope (`side_effects in (none, drains)`) covers it automatically — assuming the vendor labeled it correctly. Conformance tests verify they did.
2. **Subscriptions become semantic, not lexical.** "Tell me when an interconnect fails anywhere" is one query, forever — it doesn't need updating when new event types are added.
3. **Stability tiers propagate from the schema into runtime.** Drivers emitting `experimental` events stay invisible to prod subscribers by default; the schema's deprecation timeline becomes observable in the live fleet via `fleet.discover("rpc.labels.stability=deprecated")`.
