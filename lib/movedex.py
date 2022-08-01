import numbers
from lib.pokeapi import PokeAPI
from lib.generation import Generation, VersionTable

class Move:
    def __init__(self, raw_move: dict):
        self.name = raw_move["name"]
        self.type = raw_move["type"]
        self.accuracy = raw_move["accuracy"] if raw_move["accuracy"] != None else 100
        self.power = raw_move["power"] if raw_move["power"] != None else 0
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

class MovePool(object):
    def _has_direct_upgrade(self, move: Move):
        for other_move in self:
            if move == other_move:
                continue
            _, superior_move = move.compare_to(other_move)
            if superior_move == other_move:
                print(move.name, "upgrades into", superior_move.name)
                return True
        return False

    def __init__(self, movedex: MoveDex, move_names: list, prune_direct_upgrades: bool = True):
        self._movedex = movedex
        self._moves_by_name = dict()

        for move_name in move_names:
            self._moves_by_name[move_name] = movedex.get_move_by_name(move_name)
        
        for move_name in move_names:
            move = self._moves_by_name[move_name]
            if prune_direct_upgrades and self._has_direct_upgrade(move):
                del self._moves_by_name[move_name]
                continue

    def __iter__(self):
        return self._moves_by_name.values().__iter__()
    
    def subpool(self, filter_function):
        class Empty(object): pass
        subpool_copy = Empty()
        subpool_copy.__class__ = MovePool
        subpool_copy._movedex = self._movedex
        subpool_copy._moves_by_name = {move.name: move for move in self if filter_function(move)}
        return subpool_copy
