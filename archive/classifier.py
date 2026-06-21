from csv import Error
import json
from dataclasses import dataclass, field
from multiprocessing import Value
from pathlib import Path
from cordelia.pipeline.grouper import Group

DATA_PATH = Path(__file__).parent.parent / "data" / "_json"

# --- internal helpers ---
def _load_data(filename: str) -> dict:
   """load a json file from the data directory"""
   path = DATA_PATH / "staff" / filename
   if not path.exists():
      raise ValueError(f"Path: {path} doesn't exist")
   return json.loads(path.read_text())

# --- data models ---
INSTRUMENTs  = _load_data("INSTRUMENTs.json")
@dataclass
class Instrument:
   name:       str
   score:      str | None

MODs = _load_staff_data("MODs.json")
@dataclass
class Processor:
   name:  str
   score: str | None

GLOBAL_VARs = _load_staff_data("GLOBAL_VARs.json")
@dataclass
class GlobalVar:
   name:  str
   value: str | None

@dataclass
class Unknown:
   name:  str
   score: str | None


# type alias for return type
Classified = Instrument | Processor | GlobalVar | Unknown

# --- public api ---

def classify_staff(group: Group) -> Classified:
   name  = group.staff
   score = group.score

   if name in INSTRUMENTs:
      meta = INSTRUMENTs[name]
      return Instrument(
         name=name,
         score=score,
         path=meta.get("path", ""),
         global_var=meta.get("global_var", []),
      )

   if name in PROCESSORs:
      return Processor(name=name, score=score)

   if name in GLOBAL_VARs:
      return GlobalVar(name=name, value=score)

   return Unknown(name=name, score=score)

def classify_score(group: Group) -> Classified:
   name  = group.staff
   score = group.score

   if name in INSTRUMENTs:
      meta = INSTRUMENTs[name]
      return Instrument(
         name=name,
         score=score,
         path=meta.get("path", ""),
         global_var=meta.get("global_var", []),
      )

   if name in PROCESSORs:
      return Processor(name=name, score=score)

   if name in GLOBAL_VARs:
      return GlobalVar(name=name, value=score)

   return Unknown(name=name, score=score)


def classify_all(groups: list[Group]) -> list[Classified]:
   for g in groups:
      classify_staff(g)
      classify_score(g)
      
   return groups