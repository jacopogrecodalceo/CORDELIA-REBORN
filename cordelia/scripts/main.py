import sys
import importlib
from pathlib import Path
from loguru import logger

def list_scripts():
    """List all available scripts."""
    scripts_dir = Path(__file__).parent / "lib"
    scripts = [f.stem for f in scripts_dir.glob("*.py") if f.stem != "__init__"]
    return scripts

def run_script(script_name: str):
    """Run a specific script by name."""
    try:
        module = importlib.import_module(f"cordelia.scripts.lib.{script_name}")
        if hasattr(module, "main"):
            module.main()
        else:
            logger.info(f"Script {script_name} executed (no main function)")
    except ImportError:
        logger.error(f"Script '{script_name}' not found")
    except Exception as e:
        logger.error(f"Error in {script_name}: {e}")

def run_all_scripts():
    """Run all scripts in the lib folder."""
    scripts = list_scripts()
    for script_name in scripts:
        run_script(script_name)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No args: run all scripts
        run_all_scripts()
    else:
        # Run specific script
        script_name = sys.argv[1]
        if script_name == "--list":
            print("Available scripts:")
            for s in list_scripts():
                print(f"  - {s}")
        else:
            run_script(script_name)