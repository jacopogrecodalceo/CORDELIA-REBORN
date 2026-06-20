from rich.console import Console
from rich.theme import Theme

_theme = Theme({
   "info":       "bold bright_cyan",
   "success":    "bold bright_green",
   "warning":    "bold yellow",
   "error":      "bold bright_red",
   "muted":      "dim white",
   "nerv":       "bold white on red",
   "field":			"bold bright_cyan on black",
   "angel":      "bold magenta",
   "pilot":      "bold bright_white",
   "sync":       "bright_green",
   "desync":     "bright_red",
   "eva":        "bold magenta on black",
})

console = Console(
   theme=_theme,
   highlight=False,
   style="eva"
)