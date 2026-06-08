# Reference Driver

The base class is what the spec provides. Vendors subclass it and fill in the bodies that read their SDK.

```python
# Base — provided by the spec.
from device_connect import DeviceDriver, rpc, emit, periodic


class AcceleratorDriverBase(DeviceDriver):
    device_type = "accelerator"

    async def on_start(self):
        self.identity = {
            "device_type": "accelerator",
            "vendor":      self.VENDOR,
            "model":       self._model(),
            "device_id":   self.device_id,
            "host_id":     self.host_id,
        }

    # ── Events ──────────────────────────────────────────────
    @periodic(seconds=30)
    async def heartbeat(self):
        await self.emit_event("accelerator.heartbeat", self._snapshot())

    @emit("accelerator.interconnect_fault")
    async def interconnect_fault(self, severity, confidence, topology,
                                 vendor_evidence, normalized_effect,
                                 recommended_actions, disallowed_actions, labels):
        """Interconnect fault on a link."""

    # ── RPCs ────────────────────────────────────────────────
    @rpc(labels={"side_effects": "none"})
    async def get_health(self):
        return self._snapshot()

    @rpc(labels={"side_effects": "drains", "idempotent": True})
    async def drain_device(self, reason: str = ""):
        return await self._drain(reason)

    @rpc(labels={"side_effects": "destructive", "requires_confirmation": True}, estop=True)
    async def isolate(self, reason: str = ""):
        return await self._isolate(reason)
```

```python
# Vendor — NVIDIA. ~20 lines of SDK wiring.
import pynvml


class NvidiaAccelerator(AcceleratorDriverBase):
    VENDOR = "nvidia"

    async def on_start(self):
        pynvml.nvmlInit()
        self.h = pynvml.nvmlDeviceGetHandleByIndex(self.local_index)
        await super().on_start()

    def _model(self):
        return pynvml.nvmlDeviceGetName(self.h).decode()

    async def _drain(self, reason):
        await self._cordon(reason)              # scheduler cordon + persistence off
        return {"state": "draining", "reason": reason}

    async def _isolate(self, reason):
        await self._exec("nvidia-smi", "-i", str(self.local_index), "-p", "0")
        return {"state": "isolated", "reason": reason}
```

New silicon is a new subclass, not a new protocol. An AMD driver is the same base class with `VENDOR = "amd"` and ROCm-SMI bodies — and every consumer keying on `accelerator.interconnect_fault` or `drain_device` works on it unchanged.
