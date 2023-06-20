```sh
virtualenv env
source env/bin/activate
pip install -r requirements.txt

python3 fakeyou_infer-v2.py 0 "Path/to/the/input/audio file/Chug_Jug.wav" "Path/to/the/index file/added_IVF2933_Flat_nprobe_10.index" harvest "Path/to/the/output audio file/test_v2.wav" "Path/to/the/trained model/biggie-smalls.pth" 0.66 cuda:0 True 3 0 1 0.33

Example:

python3 fakeyou_infer-v2.py 0 "E:\codes\py39\RVC-beta\todo-songs\1111.wav" "E:\codes\py39\test-20230416b\logs\mi-test-v2\aadded_IVF677_Flat_nprobe_1_v2.index" harvest "test_v2.wav" "E:\codes\py39\test-20230416b\weights\mi-test-v2.pth" 0.66 cuda:0 True 3 0 1 0.33



```

Each argument passed to the script is used as follows:

`f0up_key`: The f0 key for the input audio file.

`input_path`: Path to the input audio file.

`index_path`: Path to the index file.

`f0method`: F0 estimation method to be used ('harvest' or 'pm').

`opt_path`: Path to the output audio file.

`model_path`: Path to the trained model.

`index_rate`: The rate for the index.

`device`: The computation device to be used ('cuda:0' for GPU or 'cpu' for CPU).

`is_half`: Boolean value indicating whether to use half precision. Use 'True' for half precision and 'False' for full precision.

`filter_radius`: The radius of the filter.

`resample_sr`: The sample rate for resampling.

`rms_mix_rate`: The RMS mix rate.

`protect`: The protect value.


See `fakeyou_infer-v2.py` for more info
