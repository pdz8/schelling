#!/bin/bash

# Variables
POC7_IP="5.1.83.225"
POC8_IP="5.1.83.226"
POC_PORT="30303"

# Aliases
alias solout="solc --binary stdout --optimize 1 --input-file"

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


