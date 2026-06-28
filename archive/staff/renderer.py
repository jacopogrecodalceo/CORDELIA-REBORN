# cordelia/renderer.py
from __future__ import annotations
from jinja2 import Environment, FileSystemLoader
from loguru import logger
from cordelia.staff.model import Staff
from cordelia.staff.const import QUALITIEs, FTGEN_SIZE
import cordelia.path

_jinja_env = Environment(
	loader=FileSystemLoader(cordelia.path.templates),
	trim_blocks=True,     # no stray newline after {% ... %}
	lstrip_blocks=True,   # no leading whitespace before {% ... %}
)


class StaffRenderer:
	__slots__ = ('env', 'score')

	def __init__(self) -> None:
		self.env = _jinja_env
		self.score: list[str] = []

	def render(self, staff: Staff) -> str:
		ctx = self._build_context(staff)

		if staff.born:
			template = self.env.get_template('born.csd.j2')
			logger.info(f'rendering born | id={staff.instr_id} | instrument={staff.instrument}')
			staff.born = False
		else:
			template = self.env.get_template('update.csd.j2')
			logger.info(f'rendering update | id={staff.instr_id}')

		output = template.render(**ctx)
		self.score.append(output)
		staff.dirty = False
		return output

	def flush(self) -> str:
		"""Return full accumulated score and reset."""
		full = '\n'.join(self.score)
		self.score.clear()
		return full

	def _build_context(self, staff: Staff) -> dict:
		return {
			'staff': staff,
			'ftgen_size': FTGEN_SIZE,
			'QUALITIEs': QUALITIEs,
			'param_data': {
				p: {
					'values': getattr(staff, p),
					'ft_num': getattr(staff, f'{p}_ft_num'),
				}
				for p in QUALITIEs
			},
		}