#!/bin/bash
#
# helper to correctly do an 'apt-get install' inside a Dockerfile's RUN
#
# the upstream mirror seems to fail a lot so this will retry 5 times
set -eu
# utility function to check if a command exists on the PATH
command_exists() { type "$1" &> /dev/null; }

# http://unix.stackexchange.com/questions/82598/how-do-i-write-a-retry-logic-in-script-to-keep-retrying-to-run-it-upto-5-times
retry() {
    local n=1
    local max=5
    local delay=5
    while true; do
        echo "Attempt ${n}/${max}: $*"
        "$@"
        local exit_code=$?

        if [ "$exit_code" -eq 0 ]; then
            echo "Attempt ${n}/${max} was successful"
            break
        elif [[ $n -lt $max ]]; then
            echo "Attempt ${n}/${max} exited non-zero ($exit_code)"
            ((n++))
            echo "Sleeping $delay seconds..."
            sleep $delay;
        else
            echo "Attempt ${n}/${max} exited non-zero ($exit_code). Giving up"
            return $exit_code
        fi
    done
}

err_report() {
    # TODO: this could be a lot better. make it red, make it print the full path to the command
    if [ -n "${SCRIPT_DIR:-}" ]; then
        >&2 echo "errexit in $SCRIPT_DIR on line $(caller). pwd=$(pwd)"
    else
        >&2 echo "errexit on line $(caller). pwd=$(pwd)"
    fi
}

trap err_report ERR

function apt-install {
    apt-get install --no-install-recommends -y "$@"
}

export DEBIAN_FRONTEND=noninteractive

# stop apt from starting processes on install
# /usr/sbin/policy-rc.d is setup to exit 101 by upstream
export RUNLEVEL=1

if [ -n "${HTTP_PROXY:-}" ]; then
    echo "Configuring apt to use HTTP_PROXY..."
    echo "Acquire::http::proxy \"$HTTP_PROXY\";" >/etc/apt/apt.conf.d/proxy
else
    echo "No HTTP_PROXY"
fi

# this is deprecated in newer versions of apt. the ubuntu image doesn't have this
if command_exists gnupg2 || command_exists gnupg || command_exists gnupg1; then
    echo "apt-key update:"
    apt-key update 2>&1
fi

echo
echo "apt-get update:"
retry apt-get update

echo
echo "Downloading packages..."
retry apt-install --download-only "$@" || true

echo
echo "Installing packages..."
apt-install "$@"

# TODO: check for an environment variable to skip this cleanup
echo
echo "Cleaning up..."
# TODO: cleanup /var/log/apt/
rm -rf /var/lib/apt/lists/*
if [ -e "/etc/apt/apt.conf.d/proxy" ]; then
    rm /etc/apt/apt.conf.d/proxy
fi

# docker's official debian and ubuntu images do apt-get clean for us