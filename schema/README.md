# schema/ — generated, do not edit

Language-neutral JSON Schema projected from the contract signatures in
[`tools/polyglot_accelerator.py`](../tools/polyglot_accelerator.py).

- `events/<event_type>.json` — JSON Schema for each event payload.
- `rpcs/<rpc_name>.json` — each RPC's labels, estop flag, and parameter schema.

Regenerate with:

```bash
python tools/export_schema.py
```

The Python `@emit` / `@rpc` signatures are the source of truth. These files are a
projection for non-Python consumers — see [`tools/README.md`](../tools/README.md).
