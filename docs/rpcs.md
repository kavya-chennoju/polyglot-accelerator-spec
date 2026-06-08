# Required RPC Contract

A `core` driver MUST expose the following RPCs with the exact names, semantics, and label envelopes defined here.

## The required set

| RPC | Purpose | Side effects | Idempotent | Confirmation |
|---|---|---|---|---|
| `get_identity()` | Return the manifest. | `none` | yes | no |
| `get_health()` | Return current telemetry snapshot (util, mem, temp, power, throttle reasons). | `none` | yes | no |
| `list_active_faults()` | Return all currently-asserted canonical events. | `none` | yes | no |
| `run_link_diagnostic(port)` | Run vendor-specific link diagnostic. Returns canonical diagnostic result. | `none` | yes | no |
| `drain_device(reason)` | Mark device unschedulable; allow current work to finish; emit a `lifecycle` event. | `drains` | yes | no |
| `cancel_drain(reason)` | Reverse a drain. | `state_change` | yes | no |
| `isolate(reason)` | Hard fence: disable from scheduler, drop from fabric where possible, fail current work. | `destructive` | yes | **yes** |
| `reset_link(port)` | Vendor-specific link reset. MUST refuse if device is not drained. | `destructive` | yes | **yes** |

## Recommended (extended) RPCs

| RPC | Purpose |
|---|---|
| `run_ecc_scrub()` | Run ECC scrubbing pass; return result. |
| `reset_device()` | Full device reset. MUST refuse if not drained. |
| `set_power_cap(watts)` | Apply a power cap. |
| `collect_dump(scope)` | Generate forensic dump (firmware state, register dump, vendor SDK telemetry archive). Returns URI to the dump artifact. |

## RPC contract requirements

- Every RPC MUST validate inputs and outputs against the schema at `https://schemas.polyglot.org/accelerator/<schema_version>/rpcs/<rpc_name>.json`.
- Every RPC MUST be idempotent unless explicitly marked otherwise. Repeating `drain_device` MUST be a no-op if the device is already draining.
- Every RPC marked `requires_confirmation` MUST accept and validate a fleet-service-issued confirmation token. Calling without a valid token MUST return a structured error `accelerator.error.requires_confirmation`.
- Every RPC marked `estop=True` MUST be exposed via the MHP estop mechanism. Drivers MUST NOT add new `estop`-tier RPCs without an RFC.
- RPCs that fail MUST return structured errors against the canonical `accelerator.error` schema, not stringified exception messages. See [Error Handling](errors.md).

## Why vendor-neutral names matter

Two drivers — one NVIDIA, one AMD — implementing `drain_device` is the deal. Consumer code keys on `drain_device`, not on `nvidia_drain` and `amd_drain`. The vendor-specific implementation (which scheduler hook, which SDK call) lives behind the canonical name. New vendors plug into the same RPC surface; consumers don't update.

## Mapping required RPCs to vendor SDKs (illustrative)

| RPC | NVIDIA implementation | AMD implementation |
|---|---|---|
| `get_health()` | NVML snapshot | ROCm-SMI snapshot |
| `run_link_diagnostic(port)` | `nvidia-smi nvlink --link <p> --diag` | `rocm-smi --showxgmierrors --xgmibwlist` |
| `drain_device(reason)` | Scheduler cordon + persistence off | Scheduler cordon + `rocm-smi --setperflevel low` |
| `isolate(reason)` | `nvidia-smi -i <idx> -p 0` + fabric drop | `rocm-smi --setfan 0` + scheduler ban |
| `reset_link(port)` | `nvidia-smi nvlink --reset <port>` | `rocm-smi --setlinkreset <port>` |

The names are vendor-neutral; the implementations are vendor-owned.
