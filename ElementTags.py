from enum import Enum
from colorama import Fore, Style

class ElementTag(str, Enum):
    FIRE = f"{Fore.RED}",
    WATER = f"{Style.DIM}{Fore.BLUE}",
    LIGHTNING = f"{Style.BRIGHT}{Fore.YELLOW}"