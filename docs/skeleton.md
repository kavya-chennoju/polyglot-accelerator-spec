# Reference Skeleton

The following Python skeleton satisfies the [Identity Manifest](manifest.md), [Required Events](events.md), [Required RPCs](rpcs.md), [Labels](labels.md), [Versioning](versioning.md), [Safety](safety.md), [Extensions](extensions.md), and [Error Handling](errors.md) sections at `conformance_level: core`.

Vendors subclass `AcceleratorDriverBase`, set `VENDOR`, and implement the private `_*` methods against their SDK. The base class enforces the contract; the subclass supplies the vendor-specific behavior.

```python
from device_connect import DeviceDriver, rpc, emit, periodic
from polyglot_schema.accelerator import (
    InterconnectFault, EccUncorrectable, ThermalThrottle,
    PowerThrottle, FatalFault, Heartbeat,
)


class AcceleratorDriverBase(DeviceDriver):
    device_type     = "accelerator"
    SCHEMA_VERSIONS = ["2026-06-01"]
    CONFORMANCE     = "core"

    # ── Identity (REQUIRED) ─────────────────────────────────────────
    # Identity-only. The driver discovers its fabric position internally and
    # uses that knowledge to populate per-event `topology` blocks when emitting.
    async def on_start(self):
        self.identity = {
            "device_type":       "accelerator",
            "vendor":            self.VENDOR,                    # set by subclass
            "model":             self._read_model(),             # vendor SDK
            "device_id":         self.device_id,
            "host_id":           self.host_id,
            "fw_version":        self._read_fw_version(),
            "conformance_level": self.CONFORMANCE,
            "schema_versions":   self.SCHEMA_VERSIONS,
        }
        # Internal-only: used to fill event-level `topology` per emission.
        self._fabric = self._discover_fabric_position()

    # ── Required events ─────────────────────────────────────────────
    @periodic(seconds=30)
    async def emit_heartbeat(self):
        await self.emit("accelerator.heartbeat", Heartbeat(
            severity="info", confidence=1.0,
            device=self.identity,
            normalized_effect=self._snapshot_effect(),
            vendor_evidence=self._snapshot_telemetry(),
            labels={
                "fault_class":    "lifecycle",
                "fault_domain":   "device",
                "stability":      "stable",
                "evidence_grade": "direct",
            },
            recommended_actions=[],
            disallowed_actions=[],
            lifecycle="transient",
        ))

    # Vendors implement these private hooks against their SDK ↓
    async def _poll_interconnect(self): ...
    async def _poll_ecc(self): ...
    async def _poll_thermal(self): ...
    async def _poll_power(self): ...
    async def _poll_fatal(self): ...

    # ── Required RPCs ───────────────────────────────────────────────
    @rpc(labels={"category": "query", "side_effects": "none",
                 "stability": "stable", "idempotent": True,
                 "requires_confirmation": False})
    async def get_identity(self):
        return self.identity

    @rpc(labels={"category": "query", "side_effects": "none",
                 "stability": "stable", "idempotent": True,
                 "requires_confirmation": False})
    async def get_health(self):
        return self._snapshot_telemetry()

    @rpc(labels={"category": "query", "side_effects": "none",
                 "stability": "stable", "idempotent": True,
                 "requires_confirmation": False})
    async def list_active_faults(self):
        return self._active_faults_snapshot()

    @rpc(labels={"category": "diagnostic", "side_effects": "none",
                 "stability": "stable", "idempotent": True,
                 "requires_confirmation": False})
    async def run_link_diagnostic(self, port: int):
        return self._run_vendor_link_diagnostic(port)

    @rpc(labels={"category": "remediation", "side_effects": "drains",
                 "stability": "stable", "idempotent": True,
                 "requires_confirmation": False})
    async def drain_device(self, reason: str = ""):
        return await self._vendor_drain(reason)

    @rpc(labels={"category": "remediation", "side_effects": "state_change",
                 "stability": "stable", "idempotent": True,
                 "requires_confirmation": False})
    async def cancel_drain(self, reason: str = ""):
        return await self._vendor_cancel_drain(reason)

    @rpc(estop=True,
         labels={"category": "remediation", "side_effects": "destructive",
                 "stability": "stable", "idempotent": True,
                 "requires_confirmation": True})
    async def isolate(self, reason: str = "", confirmation_token: str = None):
        self._validate_token(confirmation_token, scope="isolate")
        return await self._vendor_isolate(reason)

    @rpc(estop=True,
         labels={"category": "remediation", "side_effects": "destructive",
                 "stability": "stable", "idempotent": True,
                 "requires_confirmation": True})
    async def reset_link(self, port: int, confirmation_token: str = None):
        self._require_drained()
        self._validate_token(confirmation_token, scope=f"reset_link:{port}")
        return await self._vendor_reset_link(port)
```

## What a vendor subclass looks like

The whole point: vendors write a thin specialization that wires the base class to their SDK.

```python
import pynvml
from polyglot_accelerator_driver_base import AcceleratorDriverBase


class NvidiaAcceleratorDriver(AcceleratorDriverBase):
    VENDOR = "nvidia"

    async def on_start(self):
        pynvml.nvmlInit()
        self.h = pynvml.nvmlDeviceGetHandleByIndex(self.local_index)
        await super().on_start()

    def _read_model(self):
        return pynvml.nvmlDeviceGetName(self.h).decode()

    def _read_fw_version(self):
        return pynvml.nvmlSystemGetDriverVersion().decode()

    def _discover_fabric_position(self):
        # Internal driver state — fed into per-event topology blocks at emit time.
        return self._enumerate_nvlink_peers()

    async def _vendor_drain(self, reason):
        await self._mark_unschedulable(reason)         # k8s cordon / Slurm drain
        return {"state": "draining", "reason": reason}

    async def _vendor_isolate(self, reason):
        # Hard fence: persistence off, ban from fabric, exit from scheduler pool.
        await self._exec("nvidia-smi", "-i", str(self.local_index), "-p", "0")
        return {"state": "isolated", "reason": reason}

    # ... _vendor_reset_link, _run_vendor_link_diagnostic,
    #     _poll_interconnect, _poll_ecc, _poll_thermal, _poll_power, _poll_fatal
```

The base class is ~150 lines of contract enforcement. The vendor subclass is ~200 lines of vendor SDK wiring. New silicon means a new subclass, not a new protocol.
