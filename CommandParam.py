from abc import ABC, abstractmethod

class Argument(ABC):
    def __init__(self, value: str):
        self.value = value
        pass

    @abstractmethod
    def Get(self):
        pass

class Parameter():
    def __init__(self, name: str, parameterType: type, optional: bool):
        self.optional = bool(optional)
        self.type = parameterType
        self.name = name
        pass

    def CreateArg(self, inputStr: str) -> Argument:
        return self.type(inputStr)

class StringArgument(Argument):
    def __init__(self, value):
        super().__init__(value)

    def Get(self):
        if (not self.value.isascii):
            raise ValueError(f"Value of string argument is not a string!")
        
        return str(self.value)
    
class IntArgument(Argument):
    def __init__(self, value):
        super().__init__(value)

    def Get(self):
        if (not self.value.isnumeric):
            raise ValueError(f"Value of int argument is not an int!")
        
        return int(self.value)
