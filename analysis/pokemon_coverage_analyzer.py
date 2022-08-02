from lib.pokedb import PokeDB
from lib.pokedex import Pokemon

class PokemonNaiveCoverageAnalyzer:
    def _compute_best_multiplier(self, attacker: Pokemon, defender: Pokemon):
        attack_pool = attacker.movepool.subpool(
            lambda move: move.accuracy >= 80 and move.power > 75 and move.damage_class != "status")

        best_move_names = list()
        best_multiplier = 0
        for attack in attack_pool:
            multiplier = self._pokedb.typetable.compute_multiplier_for_move(attack.type, defender.typing)
            if attack.type in attacker.typing:
                multiplier *= 1.5

            if multiplier > best_multiplier:
                best_move_names = [attack.name]
                best_multiplier = multiplier
            elif multiplier == best_multiplier:
                best_move_names.append(attack.name)

        return best_multiplier, best_move_names
    
    def _compute_coverage_score(self, attacker: Pokemon):
        defenders = self._pokedb.pokedex.get_competitive_pokemon()
        coverage = 0
        for defender in defenders:
            multiplier, _ = self._compute_best_multiplier(attacker, defender)
            adjusted_multiplier = min(3.0, multiplier)  # Squash quad-effectiveness weight
            coverage += adjusted_multiplier ** 0.25
        return coverage

    def __init__(self, pokedb: PokeDB):
        self._pokedb = pokedb
        self._coverage_by_name = dict()

        competition = pokedb.pokedex.get_competitive_pokemon()
        for attacker in competition:
            coverage = self._compute_coverage_score(attacker)
            self._coverage_by_name[attacker.name] = coverage
        
        for attacker in sorted(competition, key=lambda pokemon: self[pokemon.name]):
            print(attacker.name, "has total offensive coverage score", self[attacker.name])

    def __getitem__(self, pokemon_name: str):
        return self._coverage_by_name[pokemon_name]

    def __iter__(self):
        return self._coverage_by_name.__iter__()