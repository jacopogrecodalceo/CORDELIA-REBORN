from loguru import logger
from pathlib import Path

src = Path(__file__).parent
main_dir = src.parent
corpus = main_dir / 'corpus'
qualities = corpus / 'qualities' 
json = corpus / '_json'

score = main_dir / 'score'

config = main_dir / 'config'
adc_dev_list = config / 'adc'
dac_dev_list = config / 'dac'

logger.debug(main_dir)
