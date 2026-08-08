#!/bin/zsh

cd "$(dirname "$0")"

{
    echo "PWD: $(pwd)"
    echo "argv0: $0"
    echo "---- ENV ----"
    env
} > "$HOME/cordelia_command_env.log"

cordelia run