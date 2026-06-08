# tools/

The contract lives as Python `@emit` / `@rpc` signatures. These tools project it
to a language-neutral form when a non-Python consumer needs it.

| File | What it is |
|---|---|
| `polyglot_accelerator.py` | Reference encoding of the contract — the standard `@emit`/`@rpc` signatures in dependency-free, introspectable form. In a real driver these come from `device-connect`; here they stand alone so tooling can walk them. |
| `export_schema.py` | Walks the contract and emits `schema/` — one JSON Schema per event, one definition (labels + parameter schema) per RPC. |

## Regenerate the schema

```bash
python tools/export_schema.py        # writes schema/events/*.json and schema/rpcs/*.json
```

Stdlib only — no dependencies. The Python signatures are the source of truth;
`schema/` is generated output (do not hand-edit).

## Downstream: typed bindings for any language

JSON Schema is the lingua franca. A non-Python consumer feeds the generated files
into an off-the-shelf generator:

```bash
# TypeScript / many langs
quicktype schema/events/accelerator.interconnect_fault.json -o InterconnectFault.ts

# Go
go-jsonschema schema/events/accelerator.interconnect_fault.json > interconnect_fault.go

# Python (round-trip, e.g. for a consumer that wants Pydantic models)
datamodel-codegen --input schema/events/ --output models.py
```

The result is typed structs for Go / Rust / TS — the consumer never touches Python.
This is the "go language-neutral anytime" escape hatch: you run it when a
non-Python vendor shows up, and not before.
