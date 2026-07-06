import re
from cordelia.models.ast import Array, Instrument, Variable, Func

REPEAT_PAT = re.compile(r"x(\d+)")

def expand_x_repeat(items: list) -> list:
   expanded = []
   i = 0
   while i < len(items):
      item = items[i]
      if i + 1 < len(items) and isinstance(items[i + 1], str):
         match = REPEAT_PAT.fullmatch(items[i + 1])
         if match:
            times = int(match.group(1))
            expanded.extend([item] * times)
            i += 2
            continue
      expanded.append(item)
      i += 1
   return expanded

def visit_list(items: list) -> list:
   expanded_items = expand_x_repeat(items)
   return expanded_items