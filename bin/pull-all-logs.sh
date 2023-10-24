#!/usr/bin/env bash
# Given a namespace and a base folder containing the runner logs for continuous tests, creates
# a storage area (folder) and:
#
#  1. pulls pod logs into storage_area/pods
#  2. copies runner logs to storage_area/runner
#
# Make sure you delete the original runner logs once this is done, as otherwise they might get copied into  more
# than one storage area.
set -e

namespace=${1}
runner_log_source=${2}

if [ -z "$namespace" ] || [ -z "$runner_log_source" ]; then
  echo "Usage: bin/process_logs.sh <namespace> <runner_logs>"
  exit 1
fi

run_id=$(date +'%Y-%m-%d-%H%M%S')
logs="data/logs/$run_id"
pod_logs="$logs/pods"
runner_logs="$logs/runner"

mkdir -p "$pod_logs"
bash ./bin/pull-pod-logs.sh "$namespace" "$pod_logs"

mkdir -p "$runner_logs"
cp "$runner_log_source"/* "$runner_logs/"