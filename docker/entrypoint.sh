#!/bin/bash
set -o errexit

case "$1" in
    sh|bash)
        set -- "$@"
    ;;
    *)
        set -- //arbitrum-scripts/scripts/arbitrum.sh "$@"
    ;;
esac

exec "$@"
