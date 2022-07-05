from text.pipeline_components.normalization.common_cleaners import collapse_whitespace
from text.pipeline_components.normalization.common_cleaners import convert_to_ascii
from text.pipeline_components.normalization.common_cleaners import lowercase

def normalize_spanish(raw_input_text: str) -> str:
    text = convert_to_ascii(raw_input_text)
    text = lowercase(text)

    # TODO: Expand abbreviations (Spanish)
    # TODO: Expand numbers (Spanish)

    text = collapse_whitespace(text)

    return text
