from roman import toRoman as to_roman
from roman import fromRoman as from_roman

from lib.pokeapi import PokeAPI

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

class VersionTable:
    def __init__(self, pokeapi: PokeAPI):
        self._table = dict()
        for version_group_header in pokeapi["version-group"]["results"]:
            version_group_name = version_group_header["name"]
            version_group_api = pokeapi["version-group/{}".format(version_group_name)]
            generation = Generation.from_str(version_group_api["generation"]["name"])
            self._table[version_group_name] = generation
    
    def version_group_to_generation(self, version_group: str):
        return self._table[version_group]