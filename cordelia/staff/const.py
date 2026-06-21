from loguru import logger
from pathlib import Path
import cordelia.path


FTGEN_SIZE = 8192
QUALITIEs = [x.stem for x in Path(cordelia.path.main_dir / 'data' / 'qualities').iterdir() if x.is_dir()]
logger.debug(QUALITIEs)