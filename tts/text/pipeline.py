from enum import Enum, auto

from tts.text.input_parsing.parser import GraphemeSquence, parse_grapheme_and_arpabet_sequence
from tts.text.normalization.english_normalization import EnglishNormalization
from tts.text.normalization.spanish_normalization import SpanishNormalization


class PipelineType(Enum):
    LEGACY_FAKEYOU = auto()
    ENGLISH_FORCED_ARPABET_V1 = auto()
    SPANISH_FORCED_ARPABET_V1 = auto()

_ENGLISH_NORMALIZER = EnglishNormalization()
_SPANISH_NORMALIZER = SpanishNormalization()

def _legacy_fakeyou_pipeline(input_text):
    """
    Legacy FakeYou.com did not do Grapheme -> Arpabet conversions automatically.
    """
    pass


def _english_forced_arpabet_v1(input_text):
    parsed_sequence = parse_grapheme_and_arpabet_sequence(input_text)
    for i in range(len(parsed_sequence)):
        subsequence = parsed_sequence[i]
        if isinstance(subsequence, GraphemeSquence):
            normalized = _ENGLISH_NORMALIZER.normalize(subsequence.sequence)
            parsed_sequence[i] = GraphemeSquence(normalized)

    integer_sequence = []
    


def _spanish_forced_arpabet_v1(input_text):
    parsed_sequence = parse_grapheme_and_arpabet_sequence(input_text)


def text_to_sequence(input_text: str, pipeline_type: PipelineType):
    if pipeline_type == PipelineType.ENGLISH_FORCED_ARPABET_V1:
        return _english_forced_arpabet_v1(input_text)
    elif pipeline_type == PipelineType.SPANISH_FORCED_ARPABET_V1:
        return _spanish_forced_arpabet_v1(input_text)
    else:
        return _legacy_fakeyou_pipeline(input_text)

