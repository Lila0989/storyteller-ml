import torch
import numpy as np

from base import ArpabetTransformer

class EnglishMixedArpabetTransformerV1(ArpabetTransformer):

    def transform_text(self, text):
        pre_sequence = self._handle_multi_lines(text)
        return self._convert_to_sequence(pre_sequence)

    def _handle_multi_lines(self, text):
        # NB: This code is adapted from vanilla Tacotron. It's not very graceful.
        pre_sequence = ''
        for line in text.split("\n"):
            if len(line) < 1:
                continue
            if line[-1] != ";":
                line = line + ";"
            pre_sequence += line

        return pre_sequence

    def _convert_to_sequence(self, pre_sequence_text):
        with torch.no_grad():
            # save VRAM by not including gradients
            sequence = np.array(text_to_sequence(pre_sequence_text, ['english_cleaners']))[None, :]
            sequence = torch.autograd.Variable(torch.from_numpy(sequence)).cuda().long()
        return sequence
