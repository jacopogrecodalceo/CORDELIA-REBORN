import re

_REPEAT_PAT = re.compile(r"x(\d+)")
_REPEAT_NUM_PAT = re.compile(r"(\d+)x(\d+)")


def expand_x_repeat(items: list) -> list:
	expanded = []
	i = 0
	while i < len(items):
		item = items[i]

		if isinstance(item, str):
			num_match = _REPEAT_NUM_PAT.fullmatch(item)
			if num_match:
				num_str, times_str = num_match.groups()
				expanded.extend([num_str] * int(times_str))
				i += 1
				continue

		next_item = items[i + 1] if i + 1 < len(items) else None
		if isinstance(next_item, str):
			rep_match = _REPEAT_PAT.fullmatch(next_item)
			if rep_match:
				times_str = rep_match.group(1)
				expanded.extend([item] * int(times_str))
				i += 2
				continue

		expanded.append(item)
		i += 1
	return expanded


def expand(items: list) -> list:
	return expand_x_repeat(items)