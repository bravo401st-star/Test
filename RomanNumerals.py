from typing import List, Tuple

ROMAN_MAP: List[Tuple[int, str]] = [
	(1000, "M"),
	(900, "CM"),
	(500, "D"),
	(400, "CD"),
	(100, "C"),
	(90, "XC"),
	(50, "L"),
	(40, "XL"),
	(10, "X"),
	(9, "IX"),
	(5, "V"),
	(4, "IV"),
	(1, "I"),
]

def IntToRoman(n: int) -> str:
	if not isinstance(n, int):
		raise TypeError("IntToRoman expects an int")
	if n <= 0 or n > 3999:
		raise ValueError("IntToRoman supports values from 1 to 3999")

	parts: List[str] = []
	remaining = n
	for value, numeral in ROMAN_MAP:
		if remaining <= 0:
			break
		count = remaining // value
		if count:
			parts.append(numeral * count)
			remaining -= value * count

	return "".join(parts)

