from src.dynamic_executor.classes.DynamicClassModule import DynamicClass

print("importing foo")
foo = "foo"


def function():
    pass


class StandardClass:
    pass


class SomeDynamicClass(DynamicClass):
    pass
