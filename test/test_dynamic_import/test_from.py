from pathlib import Path

from ImportedModule import StandardClass, SomeDynamicClass
from src.dynamic_executor.utils import get_modules
from src.dynamic_executor.utils.re_import import re_import_modules

if __name__ == "__main__":
    parent = Path(__file__).parent
    parent.joinpath("ImportedModule.py").write_text(
        parent.joinpath("ImportedModuleBackUpModified.py").read_text()
    )
    try:
        standard_instance = StandardClass()
        dynamic_instance = SomeDynamicClass()
        assert not hasattr(StandardClass, "foo")
        assert isinstance(standard_instance, StandardClass)
        assert not hasattr(SomeDynamicClass, "foo")
        assert isinstance(dynamic_instance, SomeDynamicClass)
        re_import_modules(get_modules(), locals(), globals())
        assert hasattr(StandardClass, "foo")
        assert not isinstance(standard_instance, StandardClass)
        assert hasattr(SomeDynamicClass, "foo")
        assert isinstance(dynamic_instance, SomeDynamicClass)
    finally:
        parent.joinpath("ImportedModule.py").write_text(
            parent.joinpath("ImportedModuleBackUp.py").read_text()
        )
