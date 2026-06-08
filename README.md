# Polyglot Accelerator Driver Specification

**Live docs:** https://kavya-chennoju.github.io/polyglot-accelerator-spec/

A vendor-neutral way for agents and humans to observe and control any accelerator — NVIDIA, AMD, Trainium, TPU, custom silicon — over the [device-connect](https://github.com/arm/device-connect) mesh. One canonical set of `@emit` / `@rpc` signatures across every vendor's silicon.

This repository contains the specification (Markdown) and the MkDocs Material site that publishes it.

## What this is

A driver is a device-connect driver that declares a **standard set of `@emit` and `@rpc` signatures**. The SDK builds the payloads, generates the parameter schemas, and broadcasts the manifest. Four pages:

- **Home** — the idea; what's standardized vs. vendor-owned.
- **Events** — the canonical `@emit` signatures.
- **RPCs** — the canonical `@rpc` signatures, with safety labels.
- **Reference Driver** — base class + a vendor subclass, end to end.

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

Specification changes are open PRs against this repository.

## License

Apache 2.0. See [LICENSE](LICENSE).
