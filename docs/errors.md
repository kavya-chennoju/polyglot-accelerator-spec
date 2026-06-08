# Error Handling

## Structured errors

Every RPC MUST return errors against the canonical error schema:

```json
{
  "error_code":   "accelerator.error.<category>",
  "message":      "human-readable",
  "retryable":    false,
  "vendor_error": {
    "source": "nvml | rocm-smi | neuron-cli | ...",
    "code":   "vendor-specific",
    "raw":    "any vendor payload"
  }
}
```

Stringified exception messages are a conformance failure.

## Required error categories

| Code | When |
|---|---|
| `accelerator.error.device_unreachable` | Driver lost contact with the underlying device. |
| `accelerator.error.not_drained` | RPC requires drained state but device is active. |
| `accelerator.error.requires_confirmation` | RPC needs a confirmation token. |
| `accelerator.error.disallowed_in_current_state` | RPC is currently disallowed (e.g. listed in `disallowed_actions` of an active fault). |
| `accelerator.error.vendor_sdk` | Underlying vendor SDK error. `vendor_error` block MUST be populated. |
| `accelerator.error.timeout` | Operation exceeded the driver's internal timeout. |

## Retryability

Drivers MUST set `retryable: true` only when:

- The error is recoverable without external intervention (e.g. transient SDK timeout).
- Retrying the same RPC call with the same arguments is safe.

For RPCs with `idempotent: true`, the caller may retry on `retryable: true` errors. For non-idempotent RPCs, `retryable` MUST be `false` regardless of the underlying cause.

## Example error returns

A `reset_link` call on a device that hasn't been drained:

```json
{
  "error_code": "accelerator.error.not_drained",
  "message":    "reset_link requires the device to be drained; current state is active",
  "retryable":  false,
  "vendor_error": null
}
```

A `drain_device` call that hits an NVML SDK error:

```json
{
  "error_code": "accelerator.error.vendor_sdk",
  "message":    "NVML returned NVML_ERROR_TIMEOUT after 5000ms",
  "retryable":  true,
  "vendor_error": {
    "source": "nvml",
    "code":   "NVML_ERROR_TIMEOUT",
    "raw":    "nvmlDeviceSetPersistenceMode timeout"
  }
}
```
