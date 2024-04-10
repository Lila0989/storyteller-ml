import json

import requests

url = 'http://localhost:8000/preview/'
# url = "http://207.189.112.61:31605/preview"
payload = {"style": "paper_origami", "positive_prompt": "test pos in", "negative_prompt": "test neg in"}
files = {'input_file': open('test_image.jpg', 'rb')}

response = requests.post(url, data={'request': json.dumps(payload)}, files=files)  # Use 'request': payload directly
if response.status_code == 200:
    # Success
    with open('preview_image.jpeg', 'wb') as f:
        f.write(response.content)
else:
    # Handle request error
    print(f"Request failed: {response.status_code}")
    print(response.text)
