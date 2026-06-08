# Polyglot Accelerator Driver Specification

**Live docs:** https://kavya-chennoju.github.io/polyglot-accelerator-spec/

A vendor-neutral observability and control contract for heterogeneous accelerator fleets — NVIDIA, AMD, Intel/Habana, AWS Neuron, Google TPU, Meta MTIA, custom silicon. One canonical event vocabulary, one set of RPC names, one safety model — across every vendor's silicon.

This repository contains the specification (Markdown) and the MkDocs Material site that publishes it.

## What this is

A draft RFC-style specification that every accelerator driver MUST conform to in order to participate in a Polyglot fleet. Includes:

- Identity manifest fields every driver must declare.
- Canonical event vocabulary (`accelerator.interconnect_fault`, `accelerator.ecc_uncorrectable`, etc.).
- Vendor-neutral RPC names and semantics (`run_link_diagnostic`, `drain_device`, `isolate`).
- Required label vocabulary for routing, RBAC, and discovery.
- Schema versioning, governance, and conformance testing rules.

## Local preview

```bash
git clone https://github.com/kavya-chennoju/polyglot-accelerator-spec.git
cd polyglot-accelerator-spec
pip install -r requirements.txt
mkdocs serve
# open http://127.0.0.1:8000
```

## Publishing

The docs site is built and deployed automatically by [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) on every push to `main`. GitHub Pages is configured to deploy from the GitHub Actions artifact.

## Companion artifacts

- `polyglot-accelerator` — the contract as one pip-installable package: base class, typed payloads, label enums, conformance suite. The single dependency every driver shares.
- `mhp-core` — underlying transport, discovery, security, and estop protocol.

## Contributing

Specification changes follow the RFC process documented at [Governance](https://kavya-chennoju.github.io/polyglot-accelerator-spec/governance/). RFCs are open PRs against this repository.

## License

Apache 2.0. See [LICENSE](LICENSE).
