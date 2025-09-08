import random
import math
from typing import Dict, Any, List
from resources.pokemon_data import PokemonDataResource


class BattleSimulator:
    def __init__(self, poke_resource: PokemonDataResource):
        self.resource = poke_resource
        random.seed()

    def _calc_type_multiplier(self, move_type: str, defender_types: List[str]) -> float:
        if not move_type:
            return 1.0

        relations = self.resource.get_type_damage_relations(move_type)
        mult = 1.0
        for d in defender_types:
            if d in relations["no_damage_to"]:
                mult *= 0.0
            elif d in relations["double_damage_to"]:
                mult *= 2.0
            elif d in relations["half_damage_to"]:
                mult *= 0.5
            else:
                mult *= 1.0
        return mult

    def _select_move(self, pokemon_data: Dict[str, Any]) -> Dict[str, Any]:
        moves = [m for m in pokemon_data["moves"] if m.get("power")]
        if not moves:
            if pokemon_data["moves"]:
                return pokemon_data["moves"][0]
            else:
                return {
                    "name": "struggele",
                    "power": 50,
                    "type": "normal",
                    "damage_class": "physical",
                }

        moves_sorted = sorted(moves, key=lambda x: (x.get("power") or 0), reverse=True)
        return moves_sorted[0]

    def _damage_formula(
        self,
        attacker_level: int,
        power: int,
        attack: int,
        defense: int,
        modifiers: float,
    ) -> int:
        # Damage = (((2 * Level / 5 + 2) * Power * (Atk / Def)) / 50 + 2) * Modifiers
        if defense <= 0:
            defense = 1
        base = (((2 * attacker_level) / 5 + 2) * power * (attack / defense)) / 50 + 2
        dmg = math.floor(base * modifiers)
        if dmg < 1:
            dmg = 1
        return dmg

    def simulate(
        self, p1_name: str, p2_name: str, level: int = 50, max_turns: int = 200
    ) -> Dict[str, Any]:
        p1 = self.resource.get_pokemon(p1_name.lower())
        p2 = self.resource.get_pokemon(p2_name.lower())
        if not p1 or not p2:
            raise ValueError("One or both Pokemon not found")

        def make_state(p):
            stats = p["stats"]
            return {
                "name": p["name"],
                "types": p["types"],
                "max_hp": stats.get("hp", 1),
                "hp": stats.get("hp", 1),
                "atk": stats.get("attack", 1),
                "def": stats.get("defense", 1),
                "spa": stats.get("special-attack", 1),
                "spd": stats.get("special-defense", 1),
                "spe": stats.get("speed", 1),
                "moves": p["moves"],
                "status": None,  # 'paralysis'|'burn'|'poison'
            }

        s1 = make_state(p1)
        s2 = make_state(p2)

        logs, turns = [], 1

        def scale_stats(s):
            s["max_hp"] = int(s["max_hp"] + level * 2)
            s["hp"] = s["max_hp"]
            s["atk"] = int(max(1, s["atk"] + level // 2))
            s["def"] = int(max(1, s["def"] + level // 2))
            s["spa"] = int(max(1, s["spa"] + level // 2))
            s["spd"] = int(max(1, s["spd"] + level // 2))
            s["spe"] = int(max(1, s["spe"] + level // 2))

        scale_stats(s1)
        scale_stats(s2)

        logs.append(
            f"Battle start : {s1['name'].title()} vs {s2['name'].title()} at level {level}."
        )
        while s1["hp"] > 0 and s2["hp"] > 0 and turns <= max_turns:
            logs.append(f"-- Turn {turns} --")
            m1 = self._select_move(s1)
            m2 = self._select_move(s2)

            spe1 = s1["spe"]
            spe2 = s2["spe"]
            if s1["status"] == "paralysis":
                spe1 = max(1, spe1 // 2)
            if s2["status"] == "paralysis":
                spe2 = max(1, spe2 // 2)

            # first, second = (s1, m1, s2, m2) if spe1 >= spe2 else (s2, m2, s1, m1)
            if spe1 >= spe2:
                attacker, attacker_move, defender, defender_move = s1, m1, s2, m2
            else:
                attacker, attacker_move, defender, defender_move = s2, m2, s1, m1

            def resolve_attack(att, move, defn):
                if att["hp"] <= 0:
                    return

                if att.get("status") == "paralysis":
                    if random.random() < 0.25:
                        logs.append(
                            f"{att['name'].title()} is paralyzed and can't move!"
                        )
                        return

                move_name = move.get("name", "sruggle")
                move_power = move.get("power") or 50

                move_type = move.get("type", "normal")
                damage_class = move.get("damage_class", "physical")

                if damage_class == "physical":
                    atk_stat = att["atk"]
                    def_stat = defn["def"]
                else:
                    atk_stat = att["spa"]
                    def_stat = defn["spd"]

                stab = 1.5 if move_type in att["types"] else 1.0

                type_mult = self._calc_type_multiplier(move_type, defn["types"])
                rand = random.uniform(0.85, 1.0)
                modifiers = stab * type_mult * rand
                damage = self._damage_formula(
                    level, move_power, atk_stat, def_stat, modifiers
                )
                defn["hp"] = max(0, defn["hp"] - damage)

                effectiveness = ""
                if type_mult == 0:
                    effectiveness = "It has no effect. "
                elif type_mult >= 2.0:
                    effectiveness = "It's super effective! "
                elif 0 < type_mult < 1.0:
                    effectiveness = "It's not very effective... "

                logs.append(
                    f"{att['name'].title()} used {move_name.replace('-', ' ').title()}! {defn['name'].title()} lost {damage} HP.{effectiveness} (HP left: {defn['hp']}/{defn['max_hp']})"
                )

                lname = move_name.lower()
                if "burn" in lname or "scorch" in lname and random.random() < 0.05:
                    if defn.get("status") is None:
                        defn["status"] = "burn"
                        logs.append(f"{defn['name'].title()} was burned!")

            resolve_attack(attacker, attacker_move, defender)
            if defender["hp"] <= 0:
                logs.append(f"{defender['name'].title()} fainted!")
                break

            resolve_attack(defender, defender_move, attacker)
            if attacker["hp"] <= 0:
                logs.append(f"{attacker['name'].title()} fainted!")
                break

            def apply_status(s):
                if s["hp"] <= 0:
                    return
                if s.get("status") == "burn":
                    dmg = max(1, s["max_hp"] // 16)
                    s["hp"] = max(0, s["hp"] - dmg)
                    logs.append(
                        f"{s['name'].title()} is hurt by its burn and lost {dmg} HP! (HP left: {s['hp']}/{s['max_hp']})"
                    )
                elif s.get("status") == "poison":
                    dmg = max(1, s["max_hp"] // 8)
                    s["hp"] = max(0, s["hp"] - dmg)
                    logs.append(
                        f"{s['name'].title()} is hurt by poison and lost {dmg} HP! (HP left: {s['hp']}/{s['max_hp']})"
                    )
                # paralysis has no ongoing damage

            apply_status(s1)
            apply_status(s2)

            turns += 1

        if s1["hp"] > 0 and s2["hp"] <= 0:
            winner = s1["name"]
        elif s2["hp"] > 0 and s1["hp"] <= 0:
            winner = s2["name"]
        elif s1["hp"] <= 0 and s2["hp"] <= 0:
            winner = "draw"
        else:
            # max turns reached: choose higher remaining HP
            if s1["hp"] > s2["hp"]:
                winner = s1["name"]
            elif s2["hp"] > s1["hp"]:
                winner = s2["name"]
            else:
                winner = "draw"

        logs.append(
            f"Battle ended after {turns-1} turns. Winner: {winner.title() if isinstance(winner,str) else winner}"
        )
        return {
            "winner": winner,
            "turns": turns - 1,
            "log": logs,
            "final_state": {
                "p1": {"name": s1["name"], "hp": s1["hp"]},
                "p2": {"name": s2["name"], "hp": s2["hp"]},
            },
        }
