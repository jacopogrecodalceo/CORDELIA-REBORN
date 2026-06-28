from dataclasses import dataclass, field

@dataclass
class Quality:
    _values: list[int] = field(default_factory=list, init=False)
    dirty: bool = False  # Move dirty after _values
    
    @property
    def values(self) -> list[int]:
        return self._values
    
    @values.setter
    def values(self, new_values: list[int]):
        if self._values != new_values:
            self._values = new_values
            self.dirty = True

@dataclass
class Cycle(Quality):
   pass

@dataclass
class Talea(Quality):
   pass

@dataclass
class Colores(Quality):
   pass

@dataclass
class Dur(Quality):
   pass

@dataclass
class Dyn(Quality):
   pass

@dataclass
class Env(Quality):
   pass

@dataclass
class Space(Quality):
   pass

@dataclass
class Character(Quality):
   pass