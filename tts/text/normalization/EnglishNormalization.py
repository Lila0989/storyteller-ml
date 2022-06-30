from text.normalization.BaseNormalization import BaseNormalization

class EnglishNormalization(BaseNormalization):

    def normalize(self, raw_input_text: str) -> str:
        return raw_input_text
