#!/bin/bash
set -ex

# Directory to watch
WATCH_PATH="*.py"

# Pod details
POD_NAME="$(kubectl get pods -n storyteller -l app=comfy-preview-server-madhukar-dev -o jsonpath='{.items[0].metadata.name}')"
echo "Pod name: ${POD_NAME}"
NAMESPACE="storyteller"
CONTAINER_PATH="/app"

# Debounce delay in seconds
DEBOUNCE_DELAY=2

# Function to perform rsync
sync_files() {
    echo "Syncing files..."
    # rsync -avz --include=".${WATCH_PATH}" --rsh="kubectl exec -i -n ${NAMESPACE} ${POD_NAME} --" "." "."
    kubectl cp "$1" ${NAMESPACE}/${POD_NAME}:${CONTAINER_PATH}/
    echo "Sync complete!"
}

# performing initial sync
sync_files preview_server.py
# Last sync time initialization
last_sync=$(date +%s)

inotifywait -m -e modify,create,delete --format '%w%f' "." | while read FILE
do
    if [[ $FILE != *.py ]]; then
        continue
    fi
    echo "Detected change in ${FILE}"
    current_time=$(date +%s)
    # Calculate the time elapsed since the last sync
    time_since_last_sync=$((current_time - last_sync))

    # Check if the elapsed time is less than the debounce delay
    if [ $time_since_last_sync -le $DEBOUNCE_DELAY ]; then
        # Calculate how much more to wait
        sleep_time=$((DEBOUNCE_DELAY - time_since_last_sync))
        echo "Waiting for $sleep_time seconds to debounce..."
        sleep $sleep_time
    fi

    # Update last sync time
    last_sync=$(date +%s)

    # Call the sync function
    sync_files $FILE
done
