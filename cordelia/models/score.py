from dataclasses import dataclass, field

@dataclass
class Talea:
   values: list[int]
   cycle: int

@dataclass
class Colores:
   values: list[float] = field(default_factory=lambda: [1])

@dataclass
class Dur:
   values: list[float] = field(default_factory=lambda: [1])

@dataclass
class Dyn:
   values: list[str | float] = field(default_factory=lambda: ['mf'])
   
@dataclass
class Env:
   values: list[str] = field(default_factory=lambda: ['classic'])

@dataclass
class Space:
   values: list[float] = field(default_factory=lambda: [1])

@dataclass
class Character:
   values: list[float] = field(default_factory=lambda: [1])
