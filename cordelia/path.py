from loguru import logger
from pathlib import Path

src = Path(__file__).parent
main_dir = src.parent
data = main_dir / 'corpus'
json = data / '_json'

logger.debug(main_dir)
