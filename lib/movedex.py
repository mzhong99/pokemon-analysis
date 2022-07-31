from lib.pokedb import PokeDB
from lib.generation import Generation, VersionTable

class Move:
    def __init__(self, raw_move: dict):
        self.name = raw_move["name"]
        self.type = raw_move["type"]
        self.accuracy = raw_move["accuracy"]
        self.power = raw_move["power"]
        self.damage_class = raw_move["damage_class"]

    def __repr__(self):
        return str(self.__dict__)

class MoveDex:
    def _fetch_move_from_pokedb(self, move_name: str, pokedb: PokeDB, generation: Generation):
        move_api = pokedb["move/{}".format(move_name)]

        raw_move = dict()
        raw_move["name"] = move_name

        for past_move_api in reversed(move_api["past_values"]):
            version_group_after_change = past_move_api["version_group"]["name"]
            generation_after_change = self._version_table.version_group_to_generation(version_group_after_change)
            if generation < generation_after_change:
                attrs_to_change = ["power", "accuracy"]
                for attr in attrs_to_change:
                    if past_move_api[attr] != None:
                        move_api[attr] = past_move_api[attr]

        raw_move["type"] = move_api["type"]["name"]
        raw_move["accuracy"] = move_api["accuracy"]
        raw_move["power"] = move_api["power"]
        raw_move["damage_class"] = move_api["damage_class"]["name"]

        self._table[move_name] = Move(raw_move)
        print(move_name, self._table[move_name])

    def __init__(self, pokedb: PokeDB, generation: Generation = Generation(1)):
        self._table = dict()
        self._version_table = VersionTable(pokedb)

        for gen in range(1, generation.int_val() + 1):
            new_moves_this_gen = [entry["name"] for entry in pokedb["generation/{}".format(gen)]["moves"]]
            for move_name in new_moves_this_gen:
                self._fetch_move_from_pokedb(move_name, pokedb, generation)
            