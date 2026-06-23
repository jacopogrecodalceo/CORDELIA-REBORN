from loguru import logger
from pathlib import Path

core = Path(__file__).parent
main_dir = core.parent

csound = core / 'csound'
include = csound / 'orc' / 'include.orc'

corpus = main_dir / 'corpus'
qualities = corpus / 'qualities' 
json = corpus / '_json'

templates = core / 'templates'


score = main_dir / 'score'

config = main_dir / 'config'
adc_dev_list = config / 'adc'
dac_dev_list = config / 'dac'

logger.debug(main_dir)
