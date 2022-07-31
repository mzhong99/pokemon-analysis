import numbers
from lib.pokeapi import PokeAPI
from lib.generation import Generation, VersionTable

class Move:
    def __init__(self, raw_move: dict):
        self.name = raw_move["name"]
        self.type = raw_move["type"]
        self.accuracy = raw_move["accuracy"]
        self.power = raw_move["power"]
        self.damage_class = raw_move["damage_class"]
        self.priority = raw_move["priority"]

    def __repr__(self):
        return str(self.__dict__)

    def compare_to(self, other) -> tuple:
        differences = []
        for key in self.__dict__.keys():
            if self.__dict__[key] != other.__dict__[key]:
                differences.append(key)

        superior_move = self
        # TODO: Determine actual algorithm for direct-upgrade moves
        return differences, superior_move

class MoveDex:
    def _fetch_move_from_pokeapi(self, move_name: str, pokeapi: PokeAPI, generation: Generation):
        move_api = pokeapi["move/{}".format(move_name)]

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
        raw_move["priority"] = move_api["priority"]

        self._dex_by_name[move_name] = Move(raw_move)

    def __init__(self, pokeapi: PokeAPI, generation: Generation = Generation(1)):
        self._dex_by_name = dict()
        self._version_table = VersionTable(pokeapi)

        for gen in range(1, generation.int_val() + 1):
            new_moves_this_gen = [entry["name"] for entry in pokeapi["generation/{}".format(gen)]["moves"]]
            for move_name in new_moves_this_gen:
                self._fetch_move_from_pokeapi(move_name, pokeapi, generation)
    
    def get_all_move_names(self):
        return self._dex_by_name.keys()
    
    def get_move_by_name(self, move_name: str) -> Move:
        return self._dex_by_name[move_name]

class MovePool:
    def _has_direct_upgrade(self, move: Move):
        for other_move in self.get_all_moves():
            if move == other_move:
                continue
            _, superior_move = move.compare_to(other_move)
            if superior_move == other_move:
                print(move.name, "upgrades into", superior_move.name)
                return True
        return False

    def __init__(self, movedex: MoveDex, move_names: list,
        prune_direct_upgrades: bool = True, min_accuracy: int = 85, min_power: int = 75):
        self._moves_by_name = dict()
        self._moves_by_damage_class = dict()

        for move_name in move_names:
            self._moves_by_name[move_name] = movedex.get_move_by_name(move_name)
        
        for move_name in move_names:
            move = self._moves_by_name[move_name]
            if move.accuracy != None and move.accuracy < min_accuracy:
                del self._moves_by_name[move_name]
                continue
            if move.power != None and move.power < min_power:
                del self._moves_by_name[move_name]
                continue
            if prune_direct_upgrades and self._has_direct_upgrade(move):
                del self._moves_by_name[move_name]
                continue
        
        for move in self.get_all_moves():
            self._moves_by_damage_class[move.damage_class] = move

    def get_all_moves(self):
        return [move for move in self._moves_by_name.values()]
    
    def get_moves_by_damage_class(self, damage_class: str):
        return [move for move in self._moves_by_damage_class[damage_class]]