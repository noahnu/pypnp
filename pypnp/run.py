#!/usr/bin/env python

import importlib
import inspect
import os
import runpy
import sys
from pathlib import Path


class PnPReader:
    _pnp = {}

    @classmethod
    def read_pnp_config(cls):
        config_path = Path("module.pnp")
        if not config_path.exists():
            with config_path.open("w") as f:
                f.writelines(["# file_path:module_name:target"])

        with config_path.open("r") as f:
            for line in f.readlines():
                if not line or line[0] == "#":
                    continue
                pattern, module_name, target = line.split(":")
                if module_name not in cls._pnp:
                    cls._pnp[module_name] = {}
                cls._pnp[module_name][pattern] = target.strip()

    @classmethod
    def lookup_target(cls, module_name):
        if module_name.startswith("__"):
            return None

        caller_file = os.path.relpath(cls.get_caller_file())
        if not caller_file:
            return None

        patterns = cls._pnp.get(module_name)
        if not patterns:
            return None

        for pattern in sorted(patterns.keys(), key=len, reverse=True):
            if caller_file.startswith(pattern):
                return patterns[pattern]
        return None

    @staticmethod
    def get_caller_file():
        frames = inspect.stack()
        filename = None
        for frame in frames:
            _filename = frame[0].f_code.co_filename
            if _filename == __file__:
                continue
            if "<frozen " in _filename:
                continue
            filename = _filename
            break
        return filename


class Loader(importlib.abc.Loader):
    def __init__(self, filename):
        self.filename = filename

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        with open(self.filename, "r") as f:
            data = f.read()
        exec(data, vars(module))


class Finder(importlib.abc.MetaPathFinder):
    def find_spec(fullname, path, target=None):

        filename = PnPReader.lookup_target(fullname)
        if filename:
            return importlib.util.spec_from_file_location(
                fullname, filename, loader=Loader(filename),
            )
        return None

    def invalidate_caches():
        pass


class SysModules(dict):
    def __init__(self, *args, **kwargs):
        self.update(sys.modules)
        sys.modules = self
        self._cache = {}

    def pop(self, key):
        value = self[key]
        del self[key]
        return value

    def __delitem__(self, key):
        target = PnPReader.lookup_target(key)
        if target is None:
            super().__delitem__(key)
        else:
            del self._cache[target]

    def __getitem__(self, key):
        target = PnPReader.lookup_target(key)
        if target is None:
            return super().__getitem__(key)
        return self._cache.get(target)

    def __setitem__(self, key, value):
        target = PnPReader.lookup_target(key)
        if target is None:
            super().__setitem__(key, value)
        else:
            self._cache[target] = value

    def __contains__(self, key):
        target = PnPReader.lookup_target(key)
        if target is None:
            return super().__contains__(key)
        return key in self._cache


def main():
    sys.meta_path.insert(0, Finder)
    PnPReader.read_pnp_config()
    sys.modules = SysModules()
    module_name = sys.argv[1]
    runpy._run_module_as_main(module_name)
