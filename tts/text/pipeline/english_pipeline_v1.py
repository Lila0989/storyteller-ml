from typing import List
from tts.text.input_parsing.parser import GraphemeSquence, ParsedSequence, parse_grapheme_and_arpabet_sequence
from tts.text.normalization.english_normalization import EnglishNormalization
from tts.text.phonetization.cmudict import CMUDict
from tts.text.phonetization.english_phonetization import EnglishPhonetization
from tts.text.pipeline.base_pipeline import BasePipeline

_ENGLISH_NORMALIZER = EnglishNormalization()

_ENGLISH_DICTIONARY = CMUDict()
_ENGLISH_PHONETIZER = EnglishPhonetization(_ENGLISH_DICTIONARY)

class EnglishPipelineV1(BasePipeline):

    def user_input_to_sequence(self, input_text: str) -> List[int]:
        """Convert raw user input into a numerical sequence for ML inference."""

        parsed_sequence = parse_grapheme_and_arpabet_sequence(input_text)

        self._normalize_graphemes(parsed_sequence)
        self._convert_phonemes(parsed_sequence)
        

        integer_sequence = []

        return integer_sequence

    def _normalize_graphemes(self, parsed_sequence: ParsedSequence):
        for i in range(len(parsed_sequence)):
            subsequence = parsed_sequence[i]
            if isinstance(subsequence, GraphemeSquence):
                normalized = _ENGLISH_NORMALIZER.normalize(subsequence.sequence)
                parsed_sequence[i] = GraphemeSquence(normalized)


    def _convert_phonemes(self, parsed_sequence: ParsedSequence):
        for i in range(len(parsed_sequence)):
            subsequence = parsed_sequence[i]
            if isinstance(subsequence, GraphemeSquence):
                converted = _ENGLISH_PHONETIZER.try_convert_to_phonemes(subsequence.sequence)
                converted = ' '.join(converted)
                parsed_sequence[i] = GraphemeSquence(converted)
