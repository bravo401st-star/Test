def MakeBar(current, maximum, width=12, fill='█', empty='░') -> str:
    filled = round((current / maximum) * width) if maximum > 0 else 0
    return fill * filled + empty * (width - filled)

def GenerateHealthbar(entity, color=None) -> str:
    import Entity
    from colorama import Fore, Style

    if isinstance(entity, Entity.AEntity):
        if color is None:
            healthPercent = entity.health / entity.maxHealth if entity.maxHealth > 0 else 0
            if healthPercent > 0.60:
                color = Fore.GREEN
            elif healthPercent >= 0.30:
                color = Fore.YELLOW
            else:
                color = Fore.RED

        return f"[HP: {color}{Style.BRIGHT}{MakeBar(entity.health, entity.maxHealth, 8)} {entity.health}/{entity.maxHealth}{Style.NORMAL}{Fore.RESET}{entity.GetBonusHealthText()}]"
    return ""

def GetRarityColor(rarity: int) -> str:
    from colorama import Fore, Style
    if rarity >= 60:   return Fore.WHITE          # Common
    if rarity >= 30:   return Fore.GREEN           # Uncommon
    if rarity >= 15:   return Fore.CYAN            # Rare
    if rarity >= 5:    return Fore.MAGENTA         # Epic
    return f"{Fore.YELLOW}{Style.BRIGHT}"          # Legendary