"""Static checkpoint inspection: all nontrivial globals become inert records."""
import collections, io, json, pickle, sys, zipfile, hashlib
from pathlib import Path

class Record:
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.args = args
        return obj
    def __init__(self, *args, **kwargs):
        self.args = args
    def __setstate__(self, state):
        if isinstance(state, dict):
            self.__dict__.update(state)
        else:
            self.state = state

class Inspector(pickle.Unpickler):
    types = {}
    def find_class(self, module, name):
        if (module, name) in [("collections", "OrderedDict")]:
            return collections.OrderedDict
        if (module, name) in [("__builtin__", "set"), ("builtins", "set")]:
            return set
        key = module + "." + name
        if key not in self.types:
            self.types[key] = type(name, (Record,), {"global_name":key})
        return self.types[key]
    def persistent_load(self, pid):
        return {"persistent_id":pid}

def walk(obj, prefix=""):
    if isinstance(obj, Record):
        yield prefix, obj
        for key, value in getattr(obj, "_modules", {}).items():
            yield from walk(value, prefix + "." + key)

def inspect(p):
    with zipfile.ZipFile(p) as z:
        data = z.read(next(n for n in z.namelist() if n.endswith("data.pkl")))
    c = Inspector(io.BytesIO(data)).load()
    m = c.get("ema") or c.get("model")
    layers = []
    for loc, mod in walk(m):
        row = {"path":loc, "type":mod.global_name}
        for key in ("groups", "in_channels", "out_channels", "kernel_size", "nc", "nl", "reg_max"):
            v = getattr(mod, key, None)
            if isinstance(v, (int, float, str, tuple, list)): row[key] = v
        layers.append(row)
    return {"file":p.name, "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
            "checkpoint_keys":list(c), "epoch":c.get("epoch"), "date":c.get("date"),
            "version":c.get("version"), "names":getattr(m, "names", None),
            "model_yaml":getattr(m, "yaml", None), "train_args":c.get("train_args"),
            "stored_metrics_UNVERIFIED":c.get("train_metrics"),
            "stored_train_results_UNVERIFIED":c.get("train_results"),
            "layers":layers, "note":"Metadata only. No tensor deserialization or execution."}

if __name__ == "__main__":
    data = [inspect(Path(p)) for p in sys.argv[1:-1]]
    Path(sys.argv[-1]).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps([{k:v for k,v in x.items() if k not in ("layers","stored_train_results_UNVERIFIED")} for x in data]))
