from tts.text.pipeline.english_pipeline_v1 import EnglishPipelineV1


class TestEnglishPipelineV1:

    def test_no_input(self):
        pipeline = EnglishPipelineV1()
        output = pipeline.user_input_to_sequence("")
        assert output == []

    def test_whitespace(self):
        pipeline = EnglishPipelineV1()
        output = pipeline.user_input_to_sequence("   \n    \t ")
        assert output == []

    def test_single_word(self):
        pipeline = EnglishPipelineV1()
        output = pipeline.user_input_to_sequence("hello")
        assert output == [106, 73, 117, 123] # NB: Arpabet encoded

    def test_two_words(self):
        pipeline = EnglishPipelineV1()
        output = pipeline.user_input_to_sequence("hello hello")
        assert output == [
            106, 73, 117, 123, # NB: Arpabet encoded
            11, # Space
            106, 73, 117, 123, # Arpabet encoded
        ]

    def test_words_and_punctuation(self):
        pipeline = EnglishPipelineV1()
        output = pipeline.user_input_to_sequence("hello friends, welcome!")
        assert output == [
            106, 73, 117, 123, # NB: Arpabet encoded
            11, # Space
            104, 130, 94, 119, 90, 146,
            11, # Space (TODO: Get rid of extraneous spaces with richer parsing)
            6,  # Comma
            11, # Space
            144, 94, 117, 116, 73, 118, 
            11, # Space
            2, # Exclamation mark
        ]
