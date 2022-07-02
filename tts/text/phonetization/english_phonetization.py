from typing import List
from tts.text.phonetization.base_phonetization import BasePhonetization
from tts.text.phonetization.cmudict import CMUDict

class EnglishPhonetization(BasePhonetization):

    def __init__(self, phoneme_dictionary: CMUDict):
        super().__init__(phoneme_dictionary)

    def convert_to_phonemes(self, grapheme_sequence: str) -> List[str]:
        words = self._split_grapheme_sentence_to_words(grapheme_sequence)
        converted_words = []

        for word in words:
            maybe_phonemes = self.phoneme_dictionary.lookup(word)
            if maybe_phonemes:
                # NB: Dictionary returns a list of possible matches. 
                # We'll just use the first.
                converted_words.append(maybe_phonemes[0])
            else:
                # TODO: Use g2p prediction to predict the phonemes.
                converted_words.append(word)

        return converted_words
