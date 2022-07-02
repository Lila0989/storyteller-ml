from tts.text.normalization.base_normalization import BaseNormalization

class SpanishNormalization(BaseNormalization):

    def normalize(self, raw_input_text: str) -> str:
        return raw_input_text
