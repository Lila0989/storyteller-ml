import json
import time
import requests

# TEST_INPUT_FILE = 'test_image.jpg'
TEST_INPUT_FILE = 'test_image_10pc.jpg'

# url = 'http://b3104:8005/preview/'
# url = "http://207.189.112.61:31605/preview"
# url = 'http://localhost:8000/preview/'

url = 'https://funnel.tailce84f.ts.net/preview/'
style_to_filename = {
    "anime_2_5d": "1_2.5d_anime_model.json",
    "anime_2d_flat": "2_2d_flat_anime_model.json",
    "cartoon_3d": "3_3d_cartoon_style.json",
    "comic_book": "4_comic_book_model.json",
    "anime_ghibli": "5_ghibli_anime_model.json",
    "ink_punk": "6_ink_punk.json",
    "ink_splash": "7_ink_splash.json",
    "ink_bw_style": "8_ink_w_and_b_style.json",
    "jojo_style": "9_jojo_style.json",
    "paper_origami": "10_paper_origami.json",
    # "pixel_art": "11_pixel_art.json",
    "pop_art": "12_pop_art.json",
    "realistic_1": "13_realistic_1.json",
    "realistic_2": "14_realistic_2.json",
    "anime_retro_neon": "15_retro_neon_anime_90.json",
    "anime_standard": "16_standard_anime_model.json",
}

all_styles = list(style_to_filename.keys())

import random
random.shuffle(all_styles)

styles = list(all_styles)[:6]
# random.shuffle(styles)

test_style_list = styles + styles
# for style, filename in list(style_to_filename.items())[:2]:
for style in all_styles:
    for i in range(3):
        # print(f"Testing style: {style}")
        payload = {"style": style, "positive_prompt": "test pos in", "negative_prompt": "test neg in"}
        with open(TEST_INPUT_FILE , 'rb') as input_file:
            # files = {'input_file': ('input_file', input_file, 'image/jpeg')}
            files = {'input_file':  input_file}
            execution_start_time = time.perf_counter()
            with requests.post(url, data={'request': json.dumps(payload)}, files=files) as response:
                if response.status_code == 200:
                    # write output file suffixed with timestamp
                    timestamp = time.strftime('%Y%m%d%H%M%S')
                    with open(f'outputs/preview_image_{style}_{timestamp}.jpeg', 'wb') as f:
                        f.write(response.content)
                else:
                    # Handle request error
                    print(f"Request failed: {response.status_code}")
                    print(response.text)
            current_time = time.perf_counter()
            execution_time = current_time - execution_start_time
            print('{} executed in {:.2f} seconds'.format(style, execution_time))
