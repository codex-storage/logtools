#!/bin/bash

namespace=${1:-"codex-continuous-tests"}
output_folder=${2:./}

# List all pods in the namespace
pods=$(kubectl get pods -n "$namespace" -o jsonpath='{.items[*].metadata.name}')

for pod in $pods; do
  echo "Fetching logs for $pod..."

  # Handle pods with multiple containers
  containers=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.spec.containers[*].name}')
  for container in $containers; do
    if [ "$container" == "$pod" ]; then
      # If there's only one container, name the log file after the pod
      kubectl logs "$pod" -n "$namespace" > "${output_folder}/${pod}.log"
    else
      # If there are multiple containers, name the log file after the pod and container
      kubectl logs "$pod" -c "$container" -n "$namespace" > "${output_folder}/${pod}_${container}.log"
    fi
  done
done

echo "Done fetching logs."
