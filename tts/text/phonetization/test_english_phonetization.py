from tts.text.phonetization.cmudict import DEFAULT_CMUDICT_PATH, CMUDict
from tts.text.phonetization.english_phonetization import EnglishPhonetization

class TestEnglishPhonetization:

    def test_no_input(self):
        phoneme_dictionary = CMUDict(DEFAULT_CMUDICT_PATH)
        phonetization = EnglishPhonetization(phoneme_dictionary)
        output = phonetization.convert_to_phonemes("")
        assert output == []

    def test_all_words_in_dictionary(self):
        phoneme_dictionary = CMUDict(DEFAULT_CMUDICT_PATH)
        phonetization = EnglishPhonetization(phoneme_dictionary)
        output = phonetization.convert_to_phonemes("this is a test")
        assert output == ["DH IH1 S", "IH1 Z", "AH0", "T EH1 S T"]

    def test_most_words_in_dictionary(self):
        phoneme_dictionary = CMUDict(DEFAULT_CMUDICT_PATH)
        phonetization = EnglishPhonetization(phoneme_dictionary)
        output = phonetization.convert_to_phonemes("nonword is a test")
        assert output == ["nonword", "IH1 Z", "AH0", "T EH1 S T"]
