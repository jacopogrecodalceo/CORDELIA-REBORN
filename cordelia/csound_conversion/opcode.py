from dataclasses import dataclass
import re

@dataclass
class Opcode:
	name: str
	ins: str
	outs: str
 
OPCODE_RE = re.compile(
	r"opcode\s+(cordelia_\w+)\s*,\s*([^,]+)\s*,\s*([^\n\r]+)",
	re.MULTILINE
)

def parse(source):
	opcode = []

	for match in OPCODE_RE.finditer(source):
		name, outs, ins = match.groups()

		opcode.append(Opcode(name=name, ins=ins, outs=outs))
	assert len(opcode) == 1, "MORE THAN ONE cordelia_ opcode recognised in the file"

	return opcode[0]