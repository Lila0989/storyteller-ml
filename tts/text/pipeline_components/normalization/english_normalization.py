from tts.text.pipeline_components.normalization.base_normalization import BaseNormalization
from tts.text.pipeline_components.normalization.common_cleaners import collapse_whitespace
from tts.text.pipeline_components.normalization.common_cleaners import convert_to_ascii
from tts.text.pipeline_components.normalization.common_cleaners import lowercase

class EnglishNormalization(BaseNormalization):

    def normalize(self, raw_input_text: str) -> str:
        text = convert_to_ascii(raw_input_text)
        text = lowercase(text)

        # TODO: Expand abbreviations
        # TODO: Expand numbers

        text = collapse_whitespace(text)

        return text
