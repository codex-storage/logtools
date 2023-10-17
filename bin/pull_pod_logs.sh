#!/bin/bash

NAMESPACE=${1:-"codex-continuous-tests"}

# List all pods in the namespace
pods=$(kubectl get pods -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')

for pod in $pods; do
  echo "Fetching logs for $pod..."

  # Handle pods with multiple containers
  containers=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath='{.spec.containers[*].name}')
  for container in $containers; do
    if [ "$container" == "$pod" ]; then
      # If there's only one container, name the log file after the pod
      kubectl logs $pod -n $NAMESPACE > "${1}${pod}.log"
    else
      # If there are multiple containers, name the log file after the pod and container
      kubectl logs $pod -c $container -n $NAMESPACE > "${1}${pod}_${container}.log"
    fi
  done
done

echo "Done fetching logs."
