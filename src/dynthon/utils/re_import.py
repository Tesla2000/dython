import importlib
import sys
from collections import ChainMap
from inspect import getmodule
from types import ModuleType
from typing import Callable

from .get_dynamic_classes import get_dynamic_classes
from ..classes.DynamicClassCreator import DynamicClassCreator


def re_import(
    module_name: str, dynamic_classes: dict[str, dict[str, DynamicClassCreator]]
) -> ModuleType:
    if module_name in sys.modules:
        return sys.modules[module_name]
    re_imported_module = importlib.import_module(module_name)
    for variable, dynamic_class in dynamic_classes[module_name].items():
        for module in dynamic_class._modifications[1:]:
            if module is None:
                continue
            try:
                importlib.import_module(module)
            except ModuleNotFoundError:
                continue
        new_class = getattr(re_imported_module, variable)
        for instance in dynamic_class._instances:
            instance.__class__ = new_class
        new_class._instances = dynamic_class._instances
    return re_imported_module


def get_module_variable(module: ModuleType, __locals: dict, variable: str) -> str:
    if hasattr(module, variable):
        return variable
    return next(var for var in dir(module) if __locals[variable] == getattr(module, var))


def re_import_modules(modules: dict[str, ModuleType], __locals: dict, __globals: dict):
    locals_from_modules = dict(
        (key, module)
        for key, value in __locals.items()
        if isinstance(value, Callable)
        and (module := getmodule(value))
        and module in modules.values()
    )
    globals_from_modules = dict(
        (key, module)
        for key, value in __globals.items()
        if isinstance(value, Callable)
        and (module := getmodule(value))
        and module in modules.values()
    )
    local_modules = dict(
        (key, value)
        for key, value in __locals.items()
        if isinstance(value, ModuleType) and key != "__builtins__"
    )
    global_modules = dict(
        (key, value)
        for key, value in __globals.items()
        if isinstance(value, ModuleType) and key != "__builtins__"
    )
    local_as_translations = {}
    global_as_translations = {}
    all_modules = ChainMap(local_modules, global_modules)
    for variable, module in locals_from_modules.items():
        all_modules[module.__name__] = module
        local_as_translations[variable] = get_module_variable(module, __locals, variable)
    for variable, module in globals_from_modules.items():
        all_modules[module.__name__] = module
        global_as_translations[variable] = get_module_variable(module, __globals, variable)
    dynamic_classes = {}
    for module_name, module in modules.items():
        dynamic_classes[module_name] = get_dynamic_classes(module)
        del sys.modules[module_name]
    local_modules = dict(
        (variable, re_import(module.__name__, dynamic_classes))
        for variable, module in local_modules.items()
    )
    global_modules = dict(
        (variable, re_import(module.__name__, dynamic_classes))
        for variable, module in global_modules.items()
    )
    locals_from_modules = dict(
        (variable, getattr(re_import(module.__name__, dynamic_classes), local_as_translations[variable]))
        for variable, module in locals_from_modules.items()
    )
    globals_from_modules = dict(
        (variable, getattr(re_import(module.__name__, dynamic_classes), global_as_translations[variable]))
        for variable, module in globals_from_modules.items()
    )
    tuple(map(importlib.import_module, all_modules.keys()))
    for variable, value in locals_from_modules.items():
        __locals[variable] = value
    for variable, value in globals_from_modules.items():
        __globals[variable] = value
    for variable, module in local_modules.items():
        __locals[variable] = module
    for variable, module in global_modules.items():
        __globals[variable] = module
