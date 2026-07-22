import cordelia.pipeline.syntax as syntax
import cordelia.pipeline.analysis as analysis
from cordelia.pipeline.conversion.converter import offer

def compile(message):
	nodes = syntax.compile(message)
	nodes = analysis.compile(nodes)
	offer(nodes)

