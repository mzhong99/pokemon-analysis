from roman import toRoman as to_roman
from roman import fromRoman as from_roman

import functools

@functools.total_ordering
class Generation:
    def from_int(gen_number: int):
        return Generation(gen_number)
    
    def from_str(gen_str: str):
        return Generation(int(from_roman(gen_str.split("-")[1].upper())))

    def __init__(self, gen_number: int):
        self._gen_number = gen_number
    
    def int_val(self) -> int:
        return self._gen_number
    
    def str_val(self) -> str:
        return "generation-{}".format(to_roman(self._gen_number).lower())

    def __lt__(self, other):
        return self._gen_number < other._gen_number

    def __eq__(self, other):
        return self._gen_number == other._gen_number