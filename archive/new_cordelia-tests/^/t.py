from lark import Lark, Tree, Token
from typing import List, Union
from dataclasses import dataclass
from enum import Enum

# ============= GRAMMARS =============

INSTRUMENT_GRAMMAR = """
%import common.WS
%ignore WS

AT             : "@"
IDENT          : /[a-zA-Z0-9_]+/
COMMA          : ","
AND            : "and"

instrument_list: instrument (COMMA? AND? WS? instrument)*
instrument     : AT IDENT
"""

SCORE_GRAMMAR = """
%import common.WS
%ignore WS

INT            : /[0-9]+/
WORD           : /[a-z,]+/
NOTE           : /[a-g][b#]?[0-9]*/
DURATION       : /[0-9]+[mavd]/
LPAR           : "("
RPAR           : ")"
X              : "x"
AND            : "and"

score          : phrase (AND phrase)*
phrase         : atom+
atom           : WORD | INT | NOTE | DURATION | group
group          : LPAR phrase RPAR X INT
"""

VARIABLE_GRAMMAR = """
%import common.WS
%ignore WS

AT             : "@"
IDENT          : /[a-zA-Z0-9_]+/
value          : /[^\\n]+/

variable       : AT IDENT WS value
"""

# ============= PARSER =============

class LineType(Enum):
    INSTRUMENTS = "instruments"
    SCORE = "score"
    VARIABLE = "variable"
    EMPTY = "empty"

@dataclass
class InstrumentLine:
    instruments: List[str]

@dataclass
class ScoreLine:
    content: str
    parsed: any

@dataclass
class VariableLine:
    name: str
    value: str

class CordeliaParser:
    def __init__(self):
        self.instrument_parser = Lark(INSTRUMENT_GRAMMAR, start="instrument_list")
        self.score_parser = Lark(SCORE_GRAMMAR, start="score")
        self.variable_parser = Lark(VARIABLE_GRAMMAR, start="variable")
    
    def classify_line(self, line: str) -> LineType:
        """Classify what type of line this is"""
        line = line.strip()
        if not line:
            return LineType.EMPTY
        
        if not line.startswith('@'):
            return LineType.SCORE
        
        # Line starts with @ - need to check if it's instruments or variable
        parts = line.split()
        
        # If ALL parts start with @, it's instruments
        if all(part.startswith('@') for part in parts):
            return LineType.INSTRUMENTS
        
        # Otherwise it's a variable
        return LineType.VARIABLE
    
    def parse_line(self, line: str) -> Union[InstrumentLine, ScoreLine, VariableLine, None]:
        """Parse a single line based on its type"""
        line_type = self.classify_line(line)
        
        if line_type == LineType.INSTRUMENTS:
            tree = self.instrument_parser.parse(line)
            # Extract instrument names from the parse tree
            instruments = []
            for child in tree.children:
                # Check if it's a Tree (has data attribute) and is an instrument
                if isinstance(child, Tree) and child.data == 'instrument':
                    # Find the IDENT token in the instrument
                    for token in child.children:
                        if isinstance(token, Token) and token.type == 'IDENT':
                            instruments.append(token.value)
                # Also handle case where instrument is directly a Token
                elif isinstance(child, Token) and child.type == 'IDENT':
                    instruments.append(child.value)
            return InstrumentLine(instruments=instruments)
        
        elif line_type == LineType.VARIABLE:
            tree = self.variable_parser.parse(line)
            # variable rule has: AT, IDENT, value
            # tree.children[0] is AT token (ignore)
            # tree.children[1] is IDENT token (name)
            # tree.children[2] is value token
            name = tree.children[1].value
            value = tree.children[2].value.strip()
            return VariableLine(name=name, value=value)
        
        elif line_type == LineType.SCORE:
            try:
                tree = self.score_parser.parse(line)
                return ScoreLine(content=line, parsed=tree)
            except Exception as e:
                # Fallback for unparseable score lines
                return ScoreLine(content=line, parsed=None)
        
        return None
    
    def parse(self, text: str) -> List[Union[InstrumentLine, ScoreLine, VariableLine]]:
        """Parse entire document"""
        results = []
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            parsed = self.parse_line(line)
            if parsed:
                results.append(parsed)
        return results

# ============= USAGE =============

if __name__ == "__main__":
    parser = CordeliaParser()
    
    draft = """@cordelia
talea 3 1 in 3
@tuning 3
@pulse 120
@cordelia @toto
talea 3 2 3 in 3 and rast 3, 32 
(d4 1 3m 5a)x4 and (db4 1 2m (6a and 5a))x4
d,,, 1 2 3


@cordelia and @toto
eu 3, 9 ,9

"""
    
    results = parser.parse(draft)
    
    for result in results:
        print(result)
        print("\n")