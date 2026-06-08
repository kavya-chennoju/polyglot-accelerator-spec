"""Reference encoding of the Polyglot accelerator contract.

A dependency-free, introspectable mirror of the standard ``@emit`` / ``@rpc``
signatures shown in the spec. In a real driver these come from device-connect
(``from device_connect import DeviceDriver, emit, rpc, periodic``); here we
provide lightweight stand-ins so tooling (schema export, conformance) can walk
the contract without the full SDK installed.

The *signatures* are the contract. Everything else — wire payloads, parameter
schemas, the language-neutral JSON Schema — is projected from them.
"""
from typing import Literal, TypedDict


# ── lightweight decorators: tag metadata for introspection ───────────────────
def emit(name=None, description=None):
    def deco(fn):
        fn._pg_kind = "emit"
        fn._pg_name = name or fn.__name__
        fn._pg_description = description or (fn.__doc__ or "").strip().split("\n")[0]
        return fn
    return deco


def rpc(name=None, description=None, labels=None, estop=False):
    def deco(fn):
        fn._pg_kind = "rpc"
        fn._pg_name = name or fn.__name__
        fn._pg_description = description or (fn.__doc__ or "").strip().split("\n")[0]
        fn._pg_labels = labels or {}
        fn._pg_estop = estop
        return fn
    return deco


def periodic(seconds):
    def deco(fn):
        fn._pg_periodic = seconds
        return fn
    return deco


# ── nested payload shapes (a TypedDict projects to a nested object schema) ────
class Device(TypedDict):
    vendor: str
    model: str
    device_id: str
    host_id: str


class Topology(TypedDict):
    link_type: Literal["nvlink", "xgmi", "pcie", "infiniband", "roce"]
    local_port: str
    peer_device_id: str
    fabric_domain: str


class VendorEvidence(TypedDict):
    source: str
    code: str


class NormalizedEffect(TypedDict):
    communication_path: Literal["ok", "degraded", "failed"]
    compute_path: Literal["ok", "degraded", "failed"]
    memory_integrity: Literal["ok", "degraded", "failed"]
    bandwidth_impact: Literal["none", "possible", "probable", "confirmed"]
    job_correctness_risk: Literal["none", "unknown", "low", "medium", "high"]
    job_performance_risk: Literal["none", "low", "medium", "high"]


class EventLabels(TypedDict):
    fault_class: Literal["interconnect", "memory", "compute", "thermal", "firmware", "lifecycle"]
    fault_domain: Literal["device", "link", "host", "rack", "fabric"]


# ── the contract: the standard @emit / @rpc signatures ───────────────────────
class AcceleratorDriverBase:
    device_type = "accelerator"

    # Events ------------------------------------------------------------------
    @emit("accelerator.interconnect_fault")
    async def interconnect_fault(
        self,
        severity: Literal["info", "degraded", "critical"],
        confidence: float,
        device: Device,
        topology: Topology,
        vendor_evidence: list[VendorEvidence],
        normalized_effect: NormalizedEffect,
        recommended_actions: list[str],
        disallowed_actions: list[str],
        labels: EventLabels,
    ):
        """Interconnect fault on an intra- or inter-node link."""

    @emit("accelerator.ecc_uncorrectable")
    async def ecc_uncorrectable(
        self,
        severity: Literal["critical"],
        confidence: float,
        device: Device,
        vendor_evidence: list[VendorEvidence],
        recommended_actions: list[str],
        disallowed_actions: list[str],
        labels: EventLabels,
    ):
        """Uncorrectable ECC / DBE event."""

    @emit("accelerator.thermal_throttle")
    async def thermal_throttle(
        self,
        severity: Literal["info", "degraded", "critical"],
        confidence: float,
        device: Device,
        normalized_effect: NormalizedEffect,
        labels: EventLabels,
    ):
        """Sustained thermal throttle."""

    @emit("accelerator.power_throttle")
    async def power_throttle(
        self,
        severity: Literal["info", "degraded", "critical"],
        confidence: float,
        device: Device,
        normalized_effect: NormalizedEffect,
        labels: EventLabels,
    ):
        """Sustained power-cap throttle."""

    @emit("accelerator.fatal_fault")
    async def fatal_fault(
        self,
        severity: Literal["critical"],
        confidence: float,
        device: Device,
        vendor_evidence: list[VendorEvidence],
        recommended_actions: list[str],
        disallowed_actions: list[str],
        labels: EventLabels,
    ):
        """Fatal hardware fault (Xid 79, GPU hang)."""

    @emit("accelerator.heartbeat")
    async def heartbeat(self, device: Device, labels: EventLabels):
        """Periodic liveness + telemetry snapshot."""

    # RPCs --------------------------------------------------------------------
    @rpc(labels={"side_effects": "none"})
    async def get_health(self) -> dict:
        """Current telemetry snapshot: util, mem, temp, power, throttle reasons."""

    @rpc(labels={"side_effects": "none"})
    async def run_link_diagnostic(self, port: int) -> dict:
        """Run a vendor link diagnostic on a port."""

    @rpc(labels={"side_effects": "drains", "idempotent": True})
    async def drain_device(self, reason: str = "") -> dict:
        """Mark the device unschedulable; let current work finish."""

    @rpc(labels={"side_effects": "destructive", "requires_confirmation": True}, estop=True)
    async def reset_link(self, port: int, confirmation_token: str = "") -> dict:
        """Reset a link. Refuses unless the device is drained."""

    @rpc(labels={"side_effects": "destructive", "requires_confirmation": True}, estop=True)
    async def isolate(self, reason: str = "", confirmation_token: str = "") -> dict:
        """Hard-fence a faulting device: drop from scheduler and fabric."""
