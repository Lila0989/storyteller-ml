import requests
import argparse
import os
import json
import time

SERVER_IP = os.environ.get("SERVER_IP", "127.0.0.1:8188")
TIMEOUT_SECONDS = int(os.environ.get("TIMEOUT_SECONDS", 1000))
PROMPT_ENDPOINT = f"http://{SERVER_IP}/prompt"

def parse_args():
    parser = argparse.ArgumentParser(description='Run Comfy')
    parser.add_argument('--prompt', type=str, help='location of the prompt json', required=True)
    return parser.parse_args()

args = parse_args()

# load prompt json
file_path = args.prompt
print(f'Loading prompt json from path: {file_path}')
prompt = json.load(open(file_path))

# check the health of the server (5 second timeout)
response = requests.get(PROMPT_ENDPOINT, timeout=5)
if response.status_code == 200:
    print("Server is healthy")
else:
    print("Server is unhealthy")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")

# make sure there are no jobs already
queue_json = response.json()
if queue_json["exec_info"]["queue_remaining"]:
    print("There are jobs in the queue already. Exiting...")
    exit(1)
else:
    print("Queue is empty")


# Load prompt
p = {"prompt": prompt}
data = json.dumps(p).encode('utf-8')
# Send HTTP post request
response = requests.post(PROMPT_ENDPOINT, data=data)
if response.status_code == 200:
    print("Job enqueued successfully")
else:
    print("Job failed to queue")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

# Wait for the job to finish
print(f"Waiting for job to finish (timeout: {TIMEOUT_SECONDS} seconds)")
start_time = time.time()
# check queue endpoint in loop
while True:
    response = requests.get(PROMPT_ENDPOINT, timeout=5)
    queue_json = response.json()
    if queue_json["exec_info"]["queue_remaining"]:
        pass
    else:
        print("Job is done")
        break
    if time.time() - start_time > TIMEOUT_SECONDS:
        print("Timeout reached and job didn't finish!")
        exit(1)
    time.sleep(1)
