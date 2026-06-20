from lark import Lark, Transformer, v_args
from dataclasses import dataclass
from typing import List, Optional, Any
from pathlib import Path
# ============================================
# DATA MODELS
# ============================================

@dataclass
class Modifier:
	prefix: str  # '.' or ':'
	name: str
	args: List[str]  # positional args as strings
	kwargs: dict  # keyword args (future extension)
	
@dataclass
class Group:
	name: str
	modifiers: List[Modifier]
	score: Optional[str]

@dataclass
class Program:
	groups: List[Group]

# ============================================
# LARK GRAMMAR
# ============================================

CORDELIA_SRC_DIR = Path(__file__).parent
GRAMMAR_PATH = CORDELIA_SRC_DIR / "main.lark"
GRAMMAR = GRAMMAR_PATH.read_text()

# ============================================
# TRANSFORMER
# ============================================

class CordeliaTransformer(Transformer):
	def __init__(self):
		self.current_group = None
		self.score_buffer = []
		self.in_score = False
		
	def program(self, items):
		return Program(groups=[item for item in items if isinstance(item, Group)])
	
	def group(self, items):
		name = items[0].value
		modifiers = []
		score = None
		
		# Extract modifiers and score from items
		for item in items[1:]:
				if isinstance(item, Modifier):
					modifiers.append(item)
				elif isinstance(item, str):
					score = item.strip()
				elif isinstance(item, list):
					# Handle score as list of tokens
					score = ''.join(str(t) for t in item).strip()
		
		return Group(name=name, modifiers=modifiers, score=score)
	
	def variable(self, items):
		# Variables are just groups with a score
		name = items[0].value
		score = items[1].value if len(items) > 1 else None
		return Group(name=name, modifiers=[], score=score)
	
	def modifier(self, items):
		return items[0]
	
	def dot_modifier(self, items):
		prefix = '.'
		name = items[0].value
		args = []
		kwargs = {}
		
		# If there's an argument list
		if len(items) > 1 and items[1] is not None:
				args = items[1]
		
		return Modifier(prefix=prefix, name=name, args=args, kwargs=kwargs)
	
	def colon_modifier(self, items):
		prefix = ':'
		name = items[0].value
		args = []
		kwargs = {}
		
		if len(items) > 1 and items[1] is not None:
				args = items[1]
		
		return Modifier(prefix=prefix, name=name, args=args, kwargs=kwargs)
	
	def arg_list(self, items):
		return items
	
	def argument(self, items):
		if len(items) == 1:
				return items[0].value
		return items[0]
	
	def delimiter(self, items):
		# Just consume the delimiter, nothing to return
		return None
	
	def score(self, items):
		# Combine all score text
		return ''.join(str(item) for item in items)
	
	def SCORE_TEXT(self, items):
		return items.value
	
	def NUMBER(self, items):
		return float(items.value) if '.' in items.value else int(items.value)
	
	def STRING(self, items):
		# Remove quotes and handle escapes
		s = items.value[1:-1]
		# Simple escape handling
		s = s.replace('\\"', '"').replace("\\'", "'")
		return s
	
	def IDENTIFIER(self, items):
		return items
	
	def symbol(self, items):
		return items.value

# ============================================
# PARSER WRAPPER
# ============================================

class CordeliaParser:
	def __init__(self):
		self.parser = Lark(
				GRAMMAR,
				parser='earley',
				#transformer=CordeliaTransformer(),
				start='program',
				# Use earley for more flexibility with ambiguous grammar
				# parser='earley'  # uncomment if you have issues
		)
	
	def parse(self, code: str) -> Program:
		
		# Preprocess: handle indentation-based scores
		# This is tricky - we need to detect when score is on new line
		# with indentation
		
		return self.parser.parse(code)
# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
	parser = CordeliaParser()
	
	# Test with your examples
	test_cases = [
		"""
		@cordelia.lpf()
  :del():radio()·talea 3, 4 d#4 1 3# 4
  
@var 123
@var 123·@cordelia talea 3 2

@cordelia
talea 3  2, 1 2 3
c4 fr dorian
wn qn
mf
zeus

;comoment

@cordelia ;can i comment?
talea 3, 2, 4, {234, 3} in 4
  
		"""
  	]
	
	for i, code in enumerate(test_cases, 1):
		print(f"\n{'='*50}")
		print(f"TEST {i}:")
		print(f"{'='*50}")
		print(f"Code:\n{code}")
		try:
			result = parser.parse(code)
			print(f"\nResult:")
			print(f"{'='*50}")
			print(result.pretty(indent_str="\t"))
			print(f"{'='*50}")
		except Exception as e:
			print(f"Error: {e}")