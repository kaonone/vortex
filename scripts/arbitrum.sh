#!/bin/bash
# run the brownie script from the correct directory
cd "$(dirname "$0")/.."
exec brownie networks import network-config.yaml True && brownie compile"$@"
