"""
reader.py — cordelia block splitter
====================================

ROLE IN THE PIPELINE
--------------------
reader.py is the first stage of the cordelia pipeline. it takes a raw
cordelia source string and splits it into a list of raw block strings.
it does not interpret meaning — that is the job of classifier.py.

   INPUT STRING
         ↓
      reader.py       ← you are here
         ↓
      classifier.py
         ↓
      resolver.py
         ↓
      ...

WHAT IS A BLOCK
---------------
a block is a logical unit of cordelia code. it is either an instrument
statement or a variable declaration.

   instrument  — starts with @       @instr talea 3 4
   variable    — starts with #       #variable 3

SPLITTING RULES
---------------
@ at a token boundary always starts a new instrument block.
# at a token boundary always starts a new variable block.

a token boundary means the character is preceded by whitespace or is
the first character of the input.

# is NOT a block boundary when glued to the preceding character:
   d#4       → sharp note
   3#        → sharp modifier
   #variable → new variable block (preceded by whitespace)

instrument blocks can span multiple lines. variable blocks end at the
next @ or # token boundary.
"""

ID_INSTRUMENT = "@"
ID_VARIABLE   = "#"
SEP_SEQUENCE  = "and"
SEP_PARALLEL  = ","


def _is_at_token_boundary(source: str, pos: int) -> bool:
   """
   returns True if position pos is at a token boundary —
   i.e. preceded by whitespace or at the start of the string.
   """
   if pos == 0:
      return True
   return source[pos - 1] in (" ", "\t", "\n", "\r")


def _has_score(chunk: str) -> bool:
   """
   returns True if the last @name in the chunk has content after it —
   meaning there is a space followed by non-empty content after the last @.
   covers both "@cordelia talea" and "@cordelia @vermillon" cases.
   """
   last_at = chunk.rfind(ID_INSTRUMENT)
   if last_at == -1:
      return False
   after_name = chunk[last_at:].split()
   return len(after_name) > 1


def _is_continuation(current: str, pos: int, source: str) -> bool:
   """
   returns True if the @ at pos should be treated as a continuation
   of the current block rather than starting a new one.
   continuation happens when:
      - current block ends with a sequence separator "and"
      - current block ends with a parallel separator ","
      - the last @name in the current block has no score yet

   always returns False if the current block is a variable (#) block —
   variables always end at the next @ boundary.
   """
   stripped = current.rstrip()
   # variable blocks always end at the next @
   if stripped.lstrip().startswith(ID_VARIABLE):
      return False
   if stripped.endswith(SEP_SEQUENCE):
      return True
   if stripped.endswith(SEP_PARALLEL):
      return True
   if not _has_score(stripped):
      return True
   return False


def read(source: str) -> list[str]:
   """
   split a cordelia source string into a list of raw block strings.

   each block starts with @ (instrument) or # (variable) at a token
   boundary. blocks end when the next @ or # token boundary is found.
   # glued to a preceding character is treated as a sharp, not a boundary.

   args:
      source: raw cordelia source string, may contain newlines

   returns:
      list of stripped block strings, empty blocks excluded

   examples:
      read("@cordelia talea 3 1")
      → ["@cordelia talea 3 1"]

      read("#p 120 #bpm 60")
      → ["#p 120", "#bpm 60"]

      read("@cordelia talea 3, 4 d#4 1 3# 4 #variable 2")
      → ["@cordelia talea 3, 4 d#4 1 3# 4", "#variable 2"]

      read("@cordelia and @vermillon talea 3 1")
      → ["@cordelia and @vermillon talea 3 1"]
   """
   chunks = []
   current = []
   i = 0

   while i < len(source):
      ch = source[i]

      if ch == ID_INSTRUMENT and _is_at_token_boundary(source, i):
         buf = "".join(current)
         if buf.strip() and not _is_continuation(buf, i, source):
            chunks.append(" ".join(buf.split()))
            current = []

      elif ch == ID_VARIABLE and _is_at_token_boundary(source, i):
         buf = "".join(current)
         if buf.strip():
            chunks.append(" ".join(buf.split()))
            current = []

      current.append(ch)
      i += 1

   if current:
      chunks.append(" ".join("".join(current).split()))

   return [b for b in chunks if b]