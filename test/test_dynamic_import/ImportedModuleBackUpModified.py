from src.dynamic_executor.classes.DynamicClassModule import DynamicClass

print("importing foo")
foo = "foo"


def function():
    pass


class StandardClass:
    def foo(self):
        pass


class SomeDynamicClass(DynamicClass):
    def foo(self):
        pass
