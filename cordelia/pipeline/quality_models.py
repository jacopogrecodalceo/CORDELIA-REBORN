from dataclasses import dataclass, field
import cordelia.const

@dataclass
class Talea:
   pattern: list[int]    # [1, 0, 1, 0, ...]
   cycle:   int          # total steps

@dataclass
class Colores:
   values: list[float] = field(default_factory=lambda: [1])

@dataclass
class Dur:
   values: list[float] = field(default_factory=lambda: [1])

@dataclass
class Dyn:
   values: list[str | float] = field(default_factory=lambda: ['mf'])

   def __post_init__(self):
      for i, value in enumerate(self.values):
         if isinstance(value, str):
               try:
                  self.values[i] = cordelia.const.data.file('dyns')[value]['norm']
               except ValueError:
                  raise ValueError(value)

@dataclass
class Env:
   values: list[str] = field(default_factory=lambda: ['classic'])

@dataclass
class Space:
   values: list[float] = field(default_factory=lambda: [1])
