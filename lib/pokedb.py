from lib.generation import Generation
from lib.movedex import MoveDex
from lib.pokeapi import PokeAPI
from lib.pokedex import PokeDex
from lib.typetable import TypeTable

class PokeDB:
    def __init__(self, cache_dir: str, api_link: str, generation: Generation = Generation.from_int(1)):
        self.cache_dir = cache_dir
        self.api_link = api_link
        self.generation = generation

        self.pokeapi = PokeAPI(cache_dir, api_link)
        self.typetable = TypeTable(self.pokeapi, self.generation)
        self.movedex = MoveDex(self.pokeapi, self.generation)
        self.pokedex = PokeDex(self.pokeapi, self.movedex, self.generation)
