from lib.pokeapi import PokeAPI
from lib.generation import Generation

class TypeTable:
    def _fetch_type_from_pokedb(self, typename: str, pokedb: PokeAPI, generation: Generation):
        type_api = pokedb["type/{}".format(typename)]
        self._table[typename] = dict()

        damage_relations_api = type_api["damage_relations"]
        for past_damage_relations_api in type_api["past_damage_relations"]:
            past_generation = Generation.from_str(past_damage_relations_api["generation"]["name"])
            if generation <= past_generation:
                damage_relations_api = past_damage_relations_api["damage_relations"]
        
        type_multiplier_keys = [("double_damage_to", 2.0), ("half_damage_to", 0.5), ("no_damage_to", 0.0)]
        for multiplier_key, multiplier in type_multiplier_keys:
            for opposing_type_api in damage_relations_api[multiplier_key]:
                opposing_typename = opposing_type_api["name"]
                self._table[typename][opposing_typename] = multiplier
    
    def __init__(self, pokedb: PokeAPI, generation: Generation = Generation(1)):
        self._table = dict()
        raw_api_types = pokedb["type"]["results"]

        excluded_types = ["shadow", "unknown"]
        if generation < Generation(6):
            excluded_types.extend(["fairy"])
        if generation < Generation(2):
            excluded_types.extend(["dark", "steel"])

        for api_type_header in raw_api_types:
            typename = api_type_header["name"]
            if typename not in excluded_types:
                self._table[typename] = dict()

        for api_type_header in raw_api_types:
            typename = api_type_header["name"]
            if typename not in excluded_types:
                self._fetch_type_from_pokedb(typename, pokedb, generation)
        
        for typename_from in self._table.keys():
            for typename_to in self._table.keys():
                if typename_to not in self._table[typename_from].keys():
                    self._table[typename_from][typename_to] = 1.0

    def get_all_types(self):
        return set(self._table.keys())

    def get_super_effective_coverage(self, typename: str):
        return {key for key in self._table[typename].keys() if self._table[typename][key] > 1.0}

    def get_neutral_or_better_coverage(self, typename: str):
        return {key for key in self._table[typename].keys() if self._table[typename][key] >= 1.0}

    def compute_multiplier_for_move(self, attacking_type: str, defending_types: tuple):
        multiplier = 1.0
        for defending_typename in defending_types:
            multiplier *= self._table[attacking_type][defending_typename]
        return multiplier