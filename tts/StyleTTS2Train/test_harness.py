import wandb
from pathlib import Path
from collections import defaultdict

class TestHarness:
    def __init__(self):
        # # start a new wandb run to track this script
        wandb.init(
            # set the wandb project where this run will be logged
            project="Style TTS 2 Finetune",
            # track hyperparameters and run metadata
            config={
                "architecture": "Style TTS 2",
            }
        )
        
        self.test_text = []
        self.test_characters = []
        self.callback = None
        self.current_checkpoint = ""
        
    def log_values(self,loss_gen_all, d_loss, loss_ce, loss_dur, loss_lm, loss_norm_rec, 
                   loss_F0_rec, loss_sty, loss_diff, d_loss_slm, loss_gen_lm, iters, epoch, step, 
                   log_interval, running_loss,train_list_len,batch_size):
        wandb.log({
                'train/mel_loss': running_loss / log_interval,
                'train/gen_loss': loss_gen_all,
                'train/d_loss': d_loss,
                'train/ce_loss': loss_ce,
                'train/dur_loss': loss_dur,
                'train/slm_loss': loss_lm,
                'train/norm_loss': loss_norm_rec,
                'train/F0_loss': loss_F0_rec,
                'train/sty_loss': loss_sty,
                'train/diff_loss': loss_diff,
                'train/d_loss_slm': d_loss_slm,
                'train/gen_loss_slm': loss_gen_lm,
                'train/iters':iters,
                'epoch':epoch+1,
                'step':step,
                'total_steps':train_list_len//batch_size
            })
    
    def sample_ood_voice(self,file:str="testing.wav",sample_rate=24000,character:str="character_name",caption:str="What is supposed to be said"):
        wandb.log({character: wandb.Audio(file, sample_rate=sample_rate, caption=caption)})

    def _next_check_point_inference(self,file_input,text,checkpoint_name:str,callback):
        saved_path = callback(file_input,text,checkpoint_name)
        return saved_path
    
    def test(self,check_point:Path):
        self.test_text = TestHarness.get_lines_from_file("TestHarness/test.txt")
        self.test_characters = TestHarness.get_files_by_folder("TestHarness/")
        
        for char_name in self.test_characters.keys():
            for ls in self.test_characters[char_name]:
                for path in ls:
                    for text in self.test_text: 
                        self._next_check_point_inference(path,text,check_point,self.callback)
    
        
    def sample_list_of_characters(self,file_path:str="output/",sample_rate=24000):
        # Open the text file and read the folder names
        folder_name_and_file_name = []
        with open(file_path, 'r') as file:
            folder_names = [line.strip() for line in file]

        # Iterate over each folder name
        for folder_name in folder_names:
            # Create a Path object for the folder
            folder_path = Path(folder_name)
            
            # Check if the folder path exists and is a directory
            if folder_path.exists() and folder_path.is_dir():
                # List all files in the folder
                for file in folder_path.iterdir(): 
                    if file.is_file():
                        folder_name_and_file_name.append(Path("{folder_name}/{f}"))
            else:
                print(f"Folder {folder_name} does not exist or is not a directory.")
        
        return folder_name_and_file_name
    
    @staticmethod
    def get_lines_from_file(file_path):
        with open(file_path,'r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            return lines           
          
    @staticmethod
    def get_files_by_folder(folder_path):
        """
        Structure each folder as 
        Traverses the directory specified by folder_path and produces a dictionary with keys
        as folder names and values as lists of file paths associated with each folder.

        :param folder_path: The path to the folder to traverse.
        :return: A dictionary where each key is a folder name and each value is a list of file paths in that folder.
        """
        root_path = Path(folder_path)
        files_by_folder = defaultdict(list)

        for file in root_path.rglob('*'):
            if file.is_file():
                # Create a key with the name of the parent folder
                folder_name = file.parent.relative_to(root_path).as_posix()
                if folder_name == '':
                    folder_name = '.'  # Represent the root folder
                # Append the file path to the list of files for this folder
                files_by_folder[folder_name].append(str(file))

        # Convert defaultdict to a regular dict for the final output
        return dict(files_by_folder)

    def done(self):
        wandb.finish()

if __name__ == "__main__":
    harness = TestHarness()
    #harness.sample_ood_voice(file="testing.wav",sample_rate=24000,character="Raiden",caption="What I just Said")
    #harness.sample_list_of_characters(file_path="./output/")

    print(TestHarness.get_files_by_folder("TestHarness/"))
    print(TestHarness.get_lines_from_file("TestHarness/test.txt"))
