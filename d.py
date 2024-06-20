# Define the base class and some subclasses

class SuperClass:
    pass

class ChildAA(SuperClass):
    pass

class ChildB(SuperClass):
    pass

class OtherClass:
    pass

# Main function to test class relationships
if __name__ == "__main__":
    # Assign a class to a variable
    ClassToTest = ChildAA

    # Check if ClassToTest is a subclass of BaseClass
    print(issubclass(ClassToTest, SuperClass))  # Should print: True

    # Check if ClassToTest is exactly BaseClass
    print(ClassToTest == SuperClass)  # Should print: False

    # Assign an instance of a class to a variable
    instance = ChildAA()

    # Check if the instance is of type BaseClass
    print(isinstance(instance, SuperClass))  # Should print: True

    # Check if the type of the instance is exactly SubClassA
    print(type(instance) == ChildAA)  # Should print: True

    # Check if the instance is of type UnrelatedClass
    print(isinstance(instance, OtherClass))  # Should print: False
