from tts.text.sequencing.english_symbols_v1 import arpabet_to_sequence, symbols_to_sequence

class TestEnglishSymbols:

    def test_no_input_arpabet(self):
        output = arpabet_to_sequence('')
        assert output == []

    def test_no_input_symbols(self):
        output = symbols_to_sequence('')
        assert output == []

    def test_arpabet_word(self):
        output = arpabet_to_sequence('T EH1 S T')
        assert output == [133, 94, 131, 133]

    def test_grapheme_word(self):
        output = symbols_to_sequence('test')
        assert output == [57, 42, 56, 57]

    def test_grapheme_sentence(self):
        output = symbols_to_sequence('this is a test.')
        assert output == [57, 45, 46, 56, 11, 46, 56, 11, 38, 11, 57, 42, 56, 57, 7]