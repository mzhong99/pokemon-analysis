import sys
import argparse
import itertools

from lib.pokeapi import PokeAPI
from lib.typetable import TypeTable
from lib.pokedex import PokeDex
from lib.movedex import MoveDex

def main(args: list):
    parser = argparse.ArgumentParser(args)
    parser.add_argument("--cache-dir", "-d", default="~/.pokedb")
    parser.add_argument("--api-link", "-l", default="https://pokeapi.co/api/v2/")
    parser.add_argument("--num-moves", "-n", default=2)
    parser.add_argument("--generation", "-g", type=int, default=5)

    parsed_args = vars(parser.parse_args())
    pokeapi = PokeAPI(parsed_args["cache_dir"], parsed_args["api_link"])

    typetable = TypeTable(pokeapi)

    viable_movesets = list()
    for moveset in itertools.combinations(typetable.get_all_types(), parsed_args["num_moves"]):
        neutral_coverage = set()
        super_effective_coverage = set()

        for movetype in moveset:
            neutral_coverage.update(typetable.get_neutral_or_better_coverage(movetype))
            super_effective_coverage.update(typetable.get_super_effective_coverage(movetype))

        if neutral_coverage == typetable.get_all_types():
            viable_movesets.append({"moves": moveset, "super_effective_coverage": super_effective_coverage})
    
    viable_movesets.sort(key=lambda moveset: len(moveset["super_effective_coverage"]))

    movedex = MoveDex(pokeapi)
    pokedex = PokeDex(pokeapi, movedex)
    pokemon_by_type_distribution = pokedex.get_competitive_type_distribution()
    
    for attacking_typename in typetable.get_all_types():
        total = []
        super_effective = []
        neutrally_effective = []

        for defending_typename in pokemon_by_type_distribution.keys():
            multiplier = typetable.compute_multiplier_for_move(attacking_typename, defending_typename)
            for defending_pokemon in pokemon_by_type_distribution[defending_typename]:
                total.append(defending_pokemon.name)
                if multiplier > 1.0:
                    super_effective.append(defending_pokemon.name)
                if multiplier == 1.0:
                    neutrally_effective.append(defending_pokemon.name)

    import pprint
    the_pokemon = pokedex.get_pokemon_by_name("pikachu")
    for move in the_pokemon.movepool.subpool(lambda move: move.accuracy >= 75 and move.power >= 80):
        pprint.pprint(move)

if __name__ == "__main__":
    main(sys.argv)