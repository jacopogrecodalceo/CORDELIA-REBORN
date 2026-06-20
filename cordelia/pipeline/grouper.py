"""
grouper.py — cordelia token grouper
=====================================

ROLE IN THE PIPELINE
--------------------
grouper.py is the second stage of the cordelia pipeline. it receives
the flat parse tree from parser.py and pairs each name with its
immediately following score.

   parser.py
      ↓
   grouper.py    ← you are here
      ↓
   classifier.py

INPUT
-----
flat lark tree with alternating name and score tokens:

   name(cordelia)
   score(talea 3 1)
   name(p)
   score(120)
   name(cordelia)       ← no score, produces Group with score=None

OUTPUT
------
list of Group dataclasses:

   Group(name="cordelia", score="talea 3 1")
   Group(name="p",        score="120")
   Group(name="cordelia", score=None)

RULES
-----
- each name gets the score token that immediately follows it
- if a name is followed by another name, it gets score=None
- if a name is the last token, it gets score=None
- a score token that appears before any name is ignored
"""

from dataclasses import dataclass
from lark import Tree

@dataclass
class Group:
   name: str
   score: str | None


def _token_type(token: Tree) -> str:
   """returns the type of a token: 'name' or 'score'"""
   return token.children[0].data


def _token_value(token: Tree) -> str:
   """returns the string value of a token"""
   return str(token.children[0].children[0]).strip()


def group(tree: Tree) -> list[Group]:
   """
   pair each name token with its immediately following score token.

   args:
      tree: lark parse tree from parser.py

   returns:
      list of Group dataclasses, one per name token

   examples:
      name(cordelia) score(talea 3 1)   → Group("cordelia", "talea 3 1")
      name(cordelia) name(vermillon)   → Group("cordelia", None), Group("vermillon", None)
      name(cordelia)                    → Group("cordelia", None)
   """
   tokens = tree.children
   groups = []
   i = 0

   while i < len(tokens):
      token = tokens[i]

      if _token_type(token) == "staff":
         staff_name = _token_value(token)
         score_value = None

         # check if next token is a score
         if i + 1 < len(tokens) and _token_type(tokens[i + 1]) == "score":
            score_value = _token_value(tokens[i + 1])
            i += 1   # skip the score token

         groups.append(Group(name=staff_name, score=score_value))

      i += 1

   return groups