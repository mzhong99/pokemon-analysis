import argparse
import sys
import os

import prompt_toolkit
from prompt_toolkit.completion import FuzzyWordCompleter


from lib.pokeapi import PokeAPI

def main(args: list):
    parser = argparse.ArgumentParser(args)
    parser.add_argument("--cache-dir", "-d", default="~/.pokedb")
    parser.add_argument("--api-link", "-l", default="https://pokeapi.co/api/v2/")

    parsed_args = vars(parser.parse_args())
    pokedb = PokeAPI(parsed_args["cache_dir"], parsed_args["api_link"])

    current_path = "."

    while True:
        prompt_str = "{} > ".format(os.path.join(parsed_args["api_link"], current_path))

        completion_words = list(pokedb[current_path].keys())
        completion_words.append("exit")
        completer = FuzzyWordCompleter(completion_words)

        result = prompt_toolkit.shortcuts.prompt(prompt_str, completer=completer)

        if result == "exit":
            break
        elif result == "..":
            current_path = os.path.dirname(current_path)
        else:
            current_path = os.path.normpath(os.path.join(current_path, result))

if __name__ == "__main__":
    main(sys.argv)