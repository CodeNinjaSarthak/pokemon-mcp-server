import requests
from functools import lru_cache
from typing import Dict, Any, List
import time

POKEMON_API_URL = "https://pokeapi.co/api/v2"


class PokemonDataResource:
    def __init__(self, user_agent: str = "pokemon-mcp-server/0/1"):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    @lru_cache(maxsize=512)
    def _get_json(self, url: str) -> Dict[str, Any]:
        for _ in range(3):
            r = self.session.get(url, timeout=15)
            try:
                r.raise_for_status()
                return r.json()
            except Exception as e:
                print(f"Error fetching {url}: {r.text[:200]}")
                raise
            time.sleep(0.5)

    def get_pokemon(self, name: str) -> Dict[str, Any]:
        name = name.lower().strip()
        poke = self._get_json(f"{POKEMON_API_URL}/pokemon/{name}")
        species = self._get_json(poke["species"]["url"])

        stats = {s["stat"]["name"]: s["base_stat"] for s in poke["stats"]}

        types = [t["type"]["name"] for t in poke["types"]]

        abilities = [
            a["ability"]["name"] + (" (hidden) " if a.get("is_hidden") else "")
            for a in poke["abilities"]
        ]

        moves = []
        for m in poke["moves"]:
            move_name = m["move"]["name"]
            try:
                move_json = self._get_json(m["move"]["url"])
            except Exception:
                moves.append({"name": move_name})
                continue

            effect = ""
            for e in move_json.get("effect_entries", []):
                if e.get("language", {}).get("name") == "en":
                    effect = e.get("short_effect") or e.get("effect") or ""
                    break

            moves.append(
                {
                    "name": move_json.get("name"),
                    "power": move_json.get("power"),
                    "pp": move_json.get("pp"),
                    "type": move_json.get("type", {}).get("name"),
                    "damage_class": move_json.get("damage_class", {}).get("name"),
                    "accuracy": move_json.get("accuracy"),
                    "effect": effect,
                }
            )

        evolution_chain = {}
        if species.get("evolution_chain") and species["evolution_chain"].get("url"):
            try:
                evo_json = self._get_json(species["evolution_chain"]["url"])
                evolution_chain = self._parse_evo_chain(evo_json["chain"])
            except Exception:
                pass
        return {
            "id": poke.get("id"),
            "name": poke.get("name"),
            "height": poke.get("height"),
            "weight": poke.get("weight"),
            "base_experience": poke.get("base_experience"),
            "stats": stats,
            "types": types,
            "abilities": abilities,
            "moves": moves,
            "evolution_chain": evolution_chain,
        }

    def _parse_evo_chain(self, chain_node: Dict[str, Any]) -> List[List[str]]:
        """
        Flatten the chain into list
        """
        stages = []

        def walk(node, depth=0):
            if len(stages) <= depth:
                stages.append([])
            stages[depth].append(node["species"]["name"])
            for evo in node.get("evolves_to", []):
                walk(evo, depth + 1)

        walk(chain_node, 0)
        return stages

    @lru_cache(maxsize=128)
    def get_type_damage_relations(self, type_name: str) -> Dict[str, List[str]]:
        type_name = type_name.strip().lower()
        data = self._get_json(f"{POKEMON_API_URL}/type/{type_name}")
        rel = data.get("damage_relations", {})
        return {
            "double_damage_to": [x["name"] for x in rel.get("double_damage_to", [])],
            "half_damage_to": [x["name"] for x in rel.get("half_damage_to", [])],
            "no_damage_to": [x["name"] for x in rel.get("no_damage_to", [])],
            "double_damage_from": [
                x["name"] for x in rel.get("double_damage_from", [])
            ],
            "half_damage_from": [x["name"] for x in rel.get("half_damage_from", [])],
            "no_damage_from": [x["name"] for x in rel.get("no_damage_from", [])],
        }
