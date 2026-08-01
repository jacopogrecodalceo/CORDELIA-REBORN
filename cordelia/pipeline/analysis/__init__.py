from loguru import logger
from cordelia.models.nodes import QUALITIEs
from cordelia.pipeline.analysis.preselection import compare

from cordelia.pipeline.analysis.nodes import *

from cordelia.models.nodes import Instrument, Variable
from cordelia.models.types import QualityStage

def compile(nodes):
   nodes = compare(nodes)
   
   logger.debug(f'PRIMARY STAGE:')
   for node in nodes:
      if isinstance(node, Instrument):
         resolve_qualities(node)
         deduce_qualities(node, QualityStage.PRIMARY)
         for quality in QUALITIEs:
            getattr(node, quality).primary_process()

      elif isinstance(node, Variable):
         pass
      logger.debug(node)

   logger.debug(f'REFERENCE STAGE:')
   for node in nodes:
      if isinstance(node, Instrument):
         deduce_qualities(node, QualityStage.REFERENCE, nodes=nodes)
         for quality in QUALITIEs:
            getattr(node, quality).post_process()

      elif isinstance(node, Variable):
         pass
      logger.debug(node)

   logger.debug(f'EMIT:')
   for node in nodes:
      if isinstance(node, Instrument):
         emit_instr_name(node)
         emit_modifiers(node)
         emit_others(node)
         resolve_modifiers(node)
      elif isinstance(node, Variable):
         resolve_variable(node)
      logger.debug(node)



   return nodes