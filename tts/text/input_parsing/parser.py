"""
Parse raw text sequences into Arpabet and Grapheme sequences so that they can be 
treated independently.

Inspired by and including code from original Tacotron2 by Keith Ito.
"""

# pyright: strict

import re
from typing import List, Union

# Regular expression matching text enclosed in curly braces:
_curly_re = re.compile(r'(.*?)\{(.+?)\}(.*)')

class ArpabetSequence:
    def __init__(self, sequence: str):
        self.sequence = sequence

class GraphemeSquence:
    def __init__(self, sequence: str):
        self.sequence = sequence

ParsedSequence = List[Union[ArpabetSequence, GraphemeSquence]]

def parse_grapheme_and_arpabet_sequence(input_text: str) -> ParsedSequence:
    """
    Parse a string into a list of ArpabetSequence and GraphemeSequence so that each 
    subsequence can be treated independently.
    """
    sequence : ParsedSequence = []

    # Check for curly braces and treat their contents as ARPAbet:
    while len(input_text):
        input_text = input_text.strip()
        m = _curly_re.match(input_text)
        if not m:
            sequence.append(GraphemeSquence(input_text))
            break

        before = m.group(1).strip()
        bracketed = m.group(2).strip()
        after = m.group(3).strip()

        if before:
            sequence.append(GraphemeSquence(before))
        if bracketed:
            sequence.append(ArpabetSequence(bracketed))

        input_text = after

    return sequence