
from cordelia.pipeline.transformer import Quality
from cordelia.pipeline.deduction import deducer

@deducer
def eu(quality: Quality) -> tuple[str, Quality] | None:
   if not quality.items or quality.items[0] != "eu":
      return None
   return "eu", Quality(items=quality.items[1:])