"""Project the contract signatures to language-neutral JSON Schema.

The Python ``@emit`` / ``@rpc`` signatures in ``polyglot_accelerator.py`` are the
source of truth. This walks them and emits:

    schema/events/<event_type>.json   JSON Schema of each event payload
    schema/rpcs/<rpc_name>.json        each RPC's labels + parameter JSON Schema

A non-Python consumer (Go, Rust, TS) feeds these into an off-the-shelf codegen
(quicktype, datamodel-code-generator, go-jsonschema) to get typed bindings —
without ever touching Python.

Run:  python tools/export_schema.py [out_dir]   (default: schema)
"""
import inspect
import json
import sys
import typing
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).parent))
from polyglot_accelerator import AcceleratorDriverBase  # noqa: E402

_PY = {str: "string", int: "integer", float: "number",
       bool: "boolean", dict: "object", list: "array", type(None): "null"}


def schema_for(ann):
    origin = typing.get_origin(ann)
    if ann is type(None):
        return {"type": "null"}
    if origin is Literal:
        return {"type": "string", "enum": list(typing.get_args(ann))}
    if typing.is_typeddict(ann):
        hints = typing.get_type_hints(ann)
        return {
            "type": "object",
            "properties": {k: schema_for(v) for k, v in hints.items()},
            "required": list(hints.keys()),
            "additionalProperties": False,
        }
    if origin is list:
        args = typing.get_args(ann) or (str,)
        return {"type": "array", "items": schema_for(args[0])}
    if origin is typing.Union:
        non_none = [a for a in typing.get_args(ann) if a is not type(None)]
        return schema_for(non_none[0]) if non_none else {"type": "null"}
    return {"type": _PY.get(ann, "object")}


def _is_optional(ann):
    return typing.get_origin(ann) is typing.Union and type(None) in typing.get_args(ann)


def params_schema(fn):
    hints = typing.get_type_hints(fn)
    props, required = {}, []
    for name, p in inspect.signature(fn).parameters.items():
        if name == "self":
            continue
        ann = hints.get(name, str)
        props[name] = schema_for(ann)
        if p.default is inspect.Parameter.empty and not _is_optional(ann):
            required.append(name)
    return props, required


def main(out="schema"):
    out = Path(out)
    (out / "events").mkdir(parents=True, exist_ok=True)
    (out / "rpcs").mkdir(parents=True, exist_ok=True)
    events = rpcs = 0
    for _, fn in inspect.getmembers(AcceleratorDriverBase, inspect.isfunction):
        kind = getattr(fn, "_pg_kind", None)
        if kind == "emit":
            props, required = params_schema(fn)
            doc = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": fn._pg_name,
                "title": fn._pg_name,
                "description": fn._pg_description,
                "type": "object",
                "properties": props,
                "required": required,
                "additionalProperties": True,
            }
            (out / "events" / f"{fn._pg_name}.json").write_text(
                json.dumps(doc, indent=2) + "\n")
            events += 1
        elif kind == "rpc":
            props, required = params_schema(fn)
            doc = {
                "name": fn._pg_name,
                "description": fn._pg_description,
                "labels": fn._pg_labels,
                "estop": fn._pg_estop,
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required,
                    "additionalProperties": False,
                },
            }
            (out / "rpcs" / f"{fn._pg_name}.json").write_text(
                json.dumps(doc, indent=2) + "\n")
            rpcs += 1
    print(f"wrote {events} event schemas + {rpcs} rpc definitions -> {out}/")


if __name__ == "__main__":
    main(*sys.argv[1:])
