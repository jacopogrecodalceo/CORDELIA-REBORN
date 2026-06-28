from loguru import logger
import re
from pathlib import Path


_MACRO_WITH_ARGS = re.compile(r'#define\s+(\w+)\(([^)]+)\)\s*#(.*?)#', re.DOTALL)
_MACRO_NO_ARGS   = re.compile(r'#define\s+(\w+)\s*#(.*?)#',             re.DOTALL)

_macros_no_args:   dict[str, str]             = {}
_macros_with_args: dict[str, tuple[list, str]] = {}


def load_macros(path: Path) -> None:
	src = path.read_text(encoding='utf-8')

	for m in _MACRO_WITH_ARGS.finditer(src):
		name = m.group(1)
		args = [a.strip() for a in m.group(2).split(',')]
		body = m.group(3)
		_macros_with_args[name] = (args, body)

	for m in _MACRO_NO_ARGS.finditer(src):
		name = m.group(1)
		if name not in _macros_with_args:
			_macros_with_args[name] = ([], m.group(2))

	_macros_no_args.update({
		k: v[1] for k, v in _macros_with_args.items() if not v[0]
	})


def _expand_once(src: str) -> str:
	# parametric: $name(arg1, arg2, ...)
	def replace_with_args(m):
		name = m.group(1)
		if name not in _macros_with_args:
			return m.group(0)
		args, body = _macros_with_args[name]
		call_args = [a.strip() for a in m.group(2).split(',')]
		result = body
		for param, value in zip(args, call_args):
			result = result.replace(f'${param}', value)
		return result

	src = re.sub(r'\$(\w+)\(([^)]*)\)', replace_with_args, src)

	# no-args: $name
	def replace_no_args(m):
		name = m.group(1)
		return _macros_no_args.get(name, m.group(0))

	src = re.sub(r'\$(\w+)', replace_no_args, src)
	return src


def expand(src: str, max_passes: int = 20) -> str:
	for _ in range(max_passes):
		expanded = _expand_once(src)
		if expanded == src:
			break
		src = expanded

	return src
