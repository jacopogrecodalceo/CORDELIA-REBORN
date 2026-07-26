"""Cordelia CLI — command-line entry point for the Cordelia toolchain."""

import argparse
import importlib
import sys

# --------------------------------------------------------------------------
# make: runs the make_* build scripts under cordelia/scripts/lib
# --------------------------------------------------------------------------

MAKE_SCRIPTS = {
	"env": "cordelia.scripts.lib.make_env_json",
	"include": "cordelia.scripts.lib.make_include",
	"instr": "cordelia.scripts.lib.make_instr_json",
	"mod": "cordelia.scripts.lib.make_mod_json",
	"scala": "cordelia.scripts.lib.make_scala_json",
}


def cmd_make(args: argparse.Namespace) -> int:
	"""Run one or more make_* scripts.

	With no flags, runs all registered scripts. With one or more
	`--<name>` flags, runs only the selected ones.
	"""
	selected = [name for name in MAKE_SCRIPTS if getattr(args, name)]
	targets = selected if selected else list(MAKE_SCRIPTS)

	for name in targets:
		module_path = MAKE_SCRIPTS[name]
		print(f"-> {name} ({module_path})")
		importlib.import_module(module_path)
	return 0


def build_make_parser(subparsers: argparse._SubParsersAction) -> None:
	make_parser = subparsers.add_parser("make", help="run make_* scripts (all by default)")
	for name in MAKE_SCRIPTS:
		make_parser.add_argument(f"--{name}", action="store_true", help=f"run make_{name}_json only")
	make_parser.set_defaults(func=cmd_make)


# --------------------------------------------------------------------------
# run: launches main.py
# --------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> int:
	from main import main as run_main
	run_main()
	return 0


def build_run_parser(subparsers: argparse._SubParsersAction) -> None:
	run_parser = subparsers.add_parser("run", help="run the main Cordelia engine")
	run_parser.set_defaults(func=cmd_run)


# --------------------------------------------------------------------------
# top-level parser
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="cordelia")
	subparsers = parser.add_subparsers(dest="command", required=True)

	build_run_parser(subparsers)
	build_make_parser(subparsers)

	return parser


def main() -> None:
	parser = build_parser()
	args = parser.parse_args()
	sys.exit(args.func(args))


if __name__ == "__main__":
	main()