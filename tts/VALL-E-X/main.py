import argparse

# python3 main.py -create_prompt_with_list 20.wav 21.wav -create_prompt_name alice
# python3 main.py -use_prompt_name alice -output_file_name alice_says.wav -text "This is the text to be converted to speech."

# python3 main.py -create_prompt_with_list 20.wav 21.wav 20.wav 21.wav -create_prompt_name alice -use_prompt_name alice -output_file_name alice_says.wav -text "This is my voice."

# python3 main.py -create_prompt_with_list goku.wav -create_prompt_name goku -use_prompt_name goku -output_file_name goku_test.wav -text "oh my god krillin! where did you put my sensu beans!?"

# python3 main.py -create_prompt_with_list

from typing import List
import pathlib
import whisperx

# https://discuss.pytorch.org/t/how-to-calculate-the-gpu-memory-that-a-model-uses/157486/6 <-- for fine tuning memory usage later.

from utils.prompt_making import make_prompt
import logging

from utils.generation import SAMPLE_RATE, generate_audio, preload_models,load_models_from_mount
import soundfile as sf
import numpy as np
import torchaudio
from typing import List
import uuid
import torchaudio.transforms as T

class AudioOps():
    
    @staticmethod
    def stitch_wav_tensors_with_crossfade(wav_tensor1:np.array,wav_tensor2:np.array,sample_rate:int):
        # Load two audio signals  as NumPy tensors
        # Compute the length of the cross-fade window in samples
        fade_len = int(0.01 * sample_rate)

        # Create a cross-fade window
        fade_window = np.hanning(2*fade_len)

        # Concatenate the signals with cross-fade
        audio_out = np.concatenate((wav_tensor1[:-fade_len], 
                                    wav_tensor1[-fade_len:] * fade_window[:fade_len] + wav_tensor2[:fade_len] * fade_window[fade_len:], 
                                    wav_tensor2[fade_len:]))
        return audio_out
    
    @staticmethod
    def cut_audio_range(file_path, start_seconds, end_seconds, output_path="cut_audio.wav"):
        """
        Cuts out a specific segment from an audio file and saves the result.

        Args:
        - file_path (str): Path to the audio file from which the segment will be cut.
        - start_seconds (float): Start time of the segment to be cut out in seconds.
        - end_seconds (float): End time of the segment to be cut out in seconds.
        - output_path (str): Path to save the resulting audio. Defaults to "cut_audio.wav".
        
        Returns:
        - None
        """
        # Load the audio file
        waveform, sr = torchaudio.load(file_path)
        # Convert the range to sample indices
        start_sample = int(start_seconds * sr)
        end_sample = int(end_seconds * sr)
        cut_tensor = waveform[:,start_sample:end_sample]
        torchaudio.save(output_path, cut_tensor, sr)
        
    @staticmethod
    def stitch_wav_files_resample(root_path:pathlib.Path, files:List[str],target_sample_rate:int=SAMPLE_RATE):
        resampler = None 
        result = None
        for file in files:  
            if type(result) == type(None):
                tensor, sr = torchaudio.load(root_path / pathlib.Path(file))
                resampler = T.Resample(orig_freq=sr,new_freq=target_sample_rate) 
                resampled_tensor = resampler(tensor)
                result = resampled_tensor.squeeze()
                result = np.array(result)
            else:  
                tensor, _ = torchaudio.load(root_path / pathlib.Path(file))
                resampled_tensor = resampler(tensor)
                resampled_tensor = resampled_tensor.squeeze()
                resampled_tensor = np.array(resampled_tensor)
                result = AudioOps.stitch_wav_tensors_with_crossfade(result,resampled_tensor,sample_rate=target_sample_rate)
                
        return result
    
class VoiceDesigner():
    def __init__(self) -> None:
        # load models from host system.
        self.logger = self.setup_logger()
        
        self.mount_folder = pathlib.Path.cwd() / pathlib.Path("Vall-E-mount") 
        # Path for the inputs bunch of audio files
        self.input_path = self.mount_folder / pathlib.Path("input")
        # Path for the models to be used
        self.models_path = self.mount_folder / pathlib.Path("models") 
        # Path for the existing presets
        self.presets_path = self.mount_folder / pathlib.Path("presets")
        # Path for the new prompts created by the user
        self.prompts_path = self.mount_folder / pathlib.Path("prompts")
        # Path for the temporary files
        self.temp_path = self.mount_folder / pathlib.Path("temp")
        # Path for output
        self.output_path = self.mount_folder / pathlib.Path("output")
        # Will have to load whisper from here as well ... todo fix
        load_models_from_mount(model_path=self.models_path,
                           vocos_path=pathlib.Path("vocos-encodec-24khz"),
                           vall_e_x=pathlib.Path("vallex-checkpoint.pt"))
        
    def tts_with_prompt(self,prompt:pathlib.Path,text:str,output_file_name:str):
        # TODO Filtering bad words
        # TODO check if the files are actually wav ...
        audio_array = generate_audio(text,prompt=prompt)
        # save audio to disk
        sf.write(self.output_path / pathlib.Path(output_file_name), audio_array, SAMPLE_RATE)
     
    def create_prompt(self,audio_file_paths:List[pathlib.Path],prompt_file_name:str):
        # multiple audio files concat
        # concat audio and trim the audio if it is longer than 14-15 seconds# if prompt is too long it will error out anyways
        if len(audio_file_paths) > 0:
            # TODO: going to assume brandon renames the files as they are uploaded
            try:# ./customs/ <-- folder it adds by default until we modified.
                    # load the audio files and then concat them. 
                tensor_result = AudioOps.stitch_wav_files_resample(root_path=self.input_path,files=audio_file_paths)
                # save to disk
                generated_name = f"{uuid.uuid4()}"
                
                concat_audio_file_path = self.temp_path / pathlib.Path(f"audio_concat_{generated_name}.wav")               
                sf.write(concat_audio_file_path, tensor_result, SAMPLE_RATE)
                # save result into processing...
                # trim to 15 seconds.
                audio_cut_path = self.temp_path / pathlib.Path(f"audio_cut_{generated_name}.wav")
                AudioOps.cut_audio_range(file_path=concat_audio_file_path,start_seconds=0,end_seconds=15,output_path=audio_cut_path)
                # TODO get whisper x to work in the container and generate transcription that way or use a different container to do that work.
                make_prompt(name=prompt_file_name,audio_prompt_output_path=self.prompts_path,audio_prompt_path=audio_cut_path,transcript=None)
            except Exception as e:
                self.logger.debug(f"Exception: {e.with_traceback()}")
                raise
        else:
            self.logger.debug(f"No audio files to load")
            
    def setup_logger(self):
        # Create a logger object
        logger = logging.getLogger(__name__)

        # Set the log level
        logger.setLevel(logging.DEBUG)

        # Create a file handler to log messages to a file
        file_handler = logging.FileHandler('docker_valle-x.log')
        file_handler.setLevel(logging.DEBUG)

        # Create a console handler to log messages to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Set the formatter for the handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger


global voice_designer 
voice_designer = VoiceDesigner()

def main(args):
    print(args.create_prompt_with_list)
    print(args.create_prompt_name)
    
    print(args.text)
    print(args.use_prompt_name)
    print(args.output_file_name)
    
    if args.create_prompt_name is not None and args.create_prompt_name is not None:
        voice_designer.create_prompt(audio_file_paths=args.create_prompt_with_list,
                                     prompt_file_name=args.create_prompt_name)
    
    if args.text is not None and args.use_prompt_name is not None:
        voice_designer.tts_with_prompt(prompt=args.use_prompt_name,
                                       text=args.text,
                                       output_file_name=args.output_file_name)    

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Process a list of speaker samples for zero shot - .wav file pathes, convert text to speech, and specify language.")

    parser.add_argument('-create_prompt_with_list', metavar='prompt wav files', nargs='+', 
                        help='Takes in a list of .wav files for an audio prompt provide the absolute path. Must be less than 15 seconds otherwise will error out.')
    
    parser.add_argument('-create_prompt_name',metavar="prompt name to create",
                        help='required with -create-prompt prompt output name this will be written to the mount. In Vall-E-mount/prompts')
    
    parser.add_argument('-text', metavar='text to synthesize', type=str, 
                        help='Text to be converted to speech.')
    
    parser.add_argument("-use_prompt_name",metavar="prompt you want to use",type=str)
    
    parser.add_argument("-output_file_name",metavar="file name",type=str)
    
    args = parser.parse_args()

    main(args)

     
    
     
     