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
        assert output == [106, 73, 117, 123, 11, 106, 73, 117, 123]

    