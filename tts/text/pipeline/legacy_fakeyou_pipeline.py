from typing import List
from tts.text.pipeline.base_pipeline import BasePipeline

class LegacyFakeYouPipeline(BasePipeline):
    """
    This pipeline was in use from June 2021 to July 2022.
    In contrast to legacy "vo.codes" (2020 - 2021), it does not 
    leverage Arpabet even when models were trained with Arpabet support.
    """


    def user_input_to_sequence(self, input_text: str) -> List[int]:
        """Convert raw user input into a numerical sequence for ML inference."""
        pre_sequence = self._preprocess_text(input_text)
        return text_to_sequence(pre_sequence, ['english_cleaners'])

    def _preprocess_text(self, input_text: str, is_raw_input: bool = True) -> str:
        pre_sequence = ""
        for line in input_text.split("\n"):
            if len(line) < 1:
                continue
            if is_raw_input:
                if line[-1] != ";":
                    line = line + ";"
            else:
                pass
            pre_sequence += line
        return pre_sequence