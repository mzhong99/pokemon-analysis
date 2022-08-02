from lib.movedex import MoveDex, MovePool
from lib.pokeapi import PokeAPI
from lib.generation import Generation, VersionTable

from collections import defaultdict

class Pokemon:
    def __init__(self, dex_raw: dict, movedex: MoveDex):
        self.name = dex_raw["name"]
        self.typing = tuple(dex_raw["typing"])
        self.is_mythical = dex_raw["is_mythical"]
        self.is_legendary = dex_raw["is_legendary"]
        self.is_fully_evolved = dex_raw["is_fully_evolved"]
        self.has_evolution = not self.is_fully_evolved
        self.id = dex_raw["dex_numbers"]["national"]

        self.movepool = MovePool(movedex, dex_raw["moves"])
        self.movepool_by_acquire_method = {acquire_method: MovePool(movedex, subpool)
            for acquire_method, subpool in dex_raw["move_acquisition_methods"].items()}
    
    def __repr__(self):
        return str(self.__dict__)

class PokeDex:
    def _fetch_pokemon_from_pokeapi(self, pokemon_name: str, pokeapi: PokeAPI, generation: Generation):
        pokemon_api = pokeapi["pokemon/{}".format(pokemon_name)]
        self._raw_dex[pokemon_name] = dict()
        self._raw_dex[pokemon_name]["name"] = pokemon_name
        self._raw_dex[pokemon_name]["is_fully_evolved"] = True

        pokemon_types_api = pokemon_api["types"]
        for past_pokemon_types_api in pokemon_api["past_types"]:
            past_generation = Generation.from_str(past_pokemon_types_api["generation"]["name"])
            if generation <= past_generation:
                pokemon_types_api = past_pokemon_types_api["types"]
        
        self._raw_dex[pokemon_name]["typing"] = [type_header["type"]["name"] for type_header in pokemon_types_api]
        
        moves_by_acquisition_method = defaultdict(set)
        self._raw_dex[pokemon_name]["moves"] = set()
        for move_api in pokemon_api["moves"]:
            move_name = move_api["move"]["name"]
            for version_group_api in move_api["version_group_details"]:
                learn_method = version_group_api["move_learn_method"]["name"]
                learn_generation = self._version_table.version_group_to_generation(version_group_api["version_group"]["name"])
                if learn_generation == generation:
                    moves_by_acquisition_method[learn_method].add(move_name)
                    self._raw_dex[pokemon_name]["moves"].add(move_name)
        self._raw_dex[pokemon_name]["move_acquisition_methods"] = moves_by_acquisition_method

        pokemon_species_api = pokeapi["pokemon-species/{}".format(pokemon_name)]
        self._raw_dex[pokemon_name]["is_legendary"] = pokemon_species_api["is_legendary"]
        self._raw_dex[pokemon_name]["is_mythical"] = pokemon_species_api["is_mythical"]
        self._raw_dex[pokemon_name]["dex_numbers"] = {
            entry["pokedex"]["name"]: entry["entry_number"] for entry in pokemon_species_api["pokedex_numbers"]}

    def _mark_evolution(self, chain_node: dict):
        pokemon_name = chain_node["species"]["name"]
        if pokemon_name not in self.get_all_pokemon_names():
            return

        self._raw_dex[pokemon_name]["is_fully_evolved"] = True
        for evolution_chain_node in chain_node["evolves_to"]:
            if evolution_chain_node["species"]["name"] not in self.get_all_pokemon_names():
                continue
            self._raw_dex[pokemon_name]["is_fully_evolved"] = False
            self._mark_evolution(evolution_chain_node)

    def _postprocess_init(self, pokeapi: PokeAPI, movedex: MoveDex, generation: int):
        evolution_chain_ids = [evolink["url"].strip("/").split("/")[-1] for evolink in pokeapi["evolution-chain"]["results"]]
        for chain_id in evolution_chain_ids:
            self._mark_evolution(pokeapi["evolution-chain/{}".format(chain_id)]["chain"])
        
        for pokemon_name in self.get_all_pokemon_names():
            pokemon = Pokemon(self._raw_dex[pokemon_name], movedex)
            self._dex_by_id[pokemon.id] = pokemon
            self._dex_by_name[pokemon_name] = pokemon

    def __init__(self, pokeapi: PokeAPI, movedex: MoveDex, generation: Generation = Generation(1)):
        self._version_table = VersionTable(pokeapi)
        self._raw_dex = dict()
        self._dex_by_name = dict()
        self._dex_by_id = dict()

        for gen in range(1, generation.int_val() + 1):
            new_pokemon_this_gen = [entry["name"] for entry in pokeapi["generation/{}".format(gen)]["pokemon_species"]]
            for pokemon_name in new_pokemon_this_gen:
                self._fetch_pokemon_from_pokeapi(pokemon_name, pokeapi, generation)
        
        self._postprocess_init(pokeapi, movedex, generation)
    
    def get_all_pokemon_names(self):
        return self._raw_dex.keys()
    
    def get_pokemon_by_name(self, pokemon_name: str) -> Pokemon:
        return self._dex_by_name[pokemon_name]
    
    def get_pokemon_by_id(self, id: int) -> Pokemon:
        return self._dex_by_id[id]
    
    def get_competitive_pokemon(self):
        return self.get_pokemon_by_query(lambda pokemon:
            not pokemon.is_legendary and not pokemon.is_mythical and not pokemon.has_evolution)

    def get_pokemon_by_query(self, filter_function):
        return [pokemon for pokemon in self._dex_by_name.values() if filter_function(pokemon)]
    
    def get_competitive_type_distribution(self,
        include_mythicals: bool = False, include_legendaries: bool = False, include_not_fully_evolved: bool = False):
        competitive_pokemon = self.get_competitive_pokemon(include_mythicals, include_legendaries, include_not_fully_evolved)

        type_distribution = dict()
        for pokemon in competitive_pokemon:
            if pokemon.typing not in type_distribution.keys():
                type_distribution[pokemon.typing] = list()
            type_distribution[pokemon.typing].append(pokemon)
        return type_distribution
