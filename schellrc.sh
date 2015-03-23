#!/bin/bash

# Variables
POC8_IP="5.1.83.225"
POC9_IP="5.1.83.226"
POC_PORT="30303"

# Aliases
alias solout="solc --binary stdout --optimize 1 --input-file"
alias ethcon="eth -j -r $POC9_IP -p $POC_PORT"

# Add to PATH for convenience
if [[ -f "schellrc.sh" ]]; then
    if [[ ! $PATH =~ "$(pwd)" ]]; then
        PATH=$PATH:$(pwd)/src/pyschelling
    fi
else
    echo "Run in project root to add to PATH." >&2
fi

###########
# Functions
###########


