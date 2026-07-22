from lark import Lark
import cordelia.path

grammar = cordelia.path.grammar.read_text()
p = Lark(grammar, start="node", parser="earley", lexer="dynamic", ambiguity="resolve")

def parse(chunks: list[str]) -> list:
   """parsing each "@" chunk cordelia's line

   Args:
      source (str): each "poem" — a cordelia line

   Returns:
      list: a parser Lark list
   """
   return [p.parse(chunk) for chunk in chunks]


