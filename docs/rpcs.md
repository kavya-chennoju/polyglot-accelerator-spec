# RPCs

An RPC is a standard `@rpc` signature. Labels declare its blast radius so agents can be scoped to safe actions.

## Canonical RPCs

| RPC | `side_effects` | confirmation |
|---|---|---|
| `get_health()` | `none` | no |
| `run_link_diagnostic(port)` | `none` | no |
| `drain_device(reason)` | `drains` | no |
| `reset_link(port)` | `destructive` | yes |
| `isolate(reason)` | `destructive` | yes |

## The signatures

```python
@rpc(labels={"side_effects": "none"})
async def get_health(self):
    """Current telemetry snapshot: util, mem, temp, power, throttle reasons."""

@rpc(labels={"side_effects": "drains", "idempotent": True})
async def drain_device(self, reason: str = ""):
    """Mark the device unschedulable; let current work finish."""

@rpc(labels={"side_effects": "destructive", "requires_confirmation": True}, estop=True)
async def isolate(self, reason: str = ""):
    """Hard-fence a faulting device: drop from scheduler and fabric."""
```

The names are vendor-neutral; the bodies call the vendor SDK.

## Why the labels matter

An agent granted only `side_effects in (none, drains)` can diagnose and drain across the entire fleet but can never `isolate` or `reset_link` — regardless of which vendor's silicon it's talking to. Governance lives on the label, not on a hard-coded list of RPC names, so a new vendor's driver is covered the moment it ships.
