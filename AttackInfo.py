from ElementTags import ElementTag

class AttInfo():
    def __init__(self, damage: int, attacker = None, ignoreEvasion: bool = False) -> None:
        self.damage = damage
        self.attacker = attacker
        self.ignoresEvasion = ignoreEvasion
        self.elements: list[ElementTag] = []

    def AddElements(self, *elements: ElementTag):
        for element in elements:
            self.elements.append(element)

        return self
    
    def HasElement(self, element: ElementTag) -> bool:
        return element in self.elements