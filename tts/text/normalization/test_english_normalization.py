from tts.text.normalization.english_normalization import EnglishNormalization

class TestEnglishNormalization:

    def test_whitespace_collapse(self):
        normalizer = EnglishNormalization()
        output = normalizer.normalize(" \t \n   normalized   \n \t ")
        assert output == " normalized "

    def test_lowercase(self):
        normalizer = EnglishNormalization()
        output = normalizer.normalize("This is a test of Normalization.")
        assert output == "this is a test of normalization."
