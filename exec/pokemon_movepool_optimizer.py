import argparse
import sys

from lib.generation import Generation
from lib.pokedb import PokeDB
from analysis.pokemon_coverage_analyzer import PokemonNaiveCoverageAnalyzer

def main(args: list):
    parser = argparse.ArgumentParser(args)
    parser.add_argument("--cache-dir", "-d", default="~/.pokedb")
    parser.add_argument("--api-link", "-l", default="https://pokeapi.co/api/v2/")
    parser.add_argument("--num-moves", "-n", default=2)
    parser.add_argument("--generation", "-g", type=int, default=1)

    parsed_args = vars(parser.parse_args())
    pokedb = PokeDB(parsed_args["cache_dir"], parsed_args["api_link"], Generation(parsed_args["generation"]))
    PokemonNaiveCoverageAnalyzer(pokedb)

if __name__ == "__main__":
    main(sys.argv)