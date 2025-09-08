from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from resources.pokemon_data import PokemonDataResource
from tools.battle_simulator import BattleSimulator

app = FastAPI(title="Pokemon MCP Server")
poke_resource = PokemonDataResource()
battle_tool = BattleSimulator(poke_resource)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Pokemon MCP Server! Use /mcp/resources/pokemon_data or /mcp/tools/battle_simulator."
    }


@app.get("/mcp/resources/pokemon_data")
def get_pokemon_name(name: str):
    """
    Get Pokemon data by name.
    """
    try:
        data = poke_resource.get_pokemon(name)
        return {"resource": "pokemon_data", "name": name.lower(), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class BattleRequest(BaseModel):
    pokemon1: str
    pokemon2: str
    level: int = 50
    max_turns: int = 200


@app.post("/mcp/tools/battle_simulator")
def simulate_battle(req: BattleRequest):
    """
    Simulate a battle between 2 pokemon"""
    try:
        result = battle_tool.simulate(
            req.pokemon1, req.pokemon2, level=req.level, max_turns=req.max_turns
        )
        return {"tool": "battle_simulator", "params": req.dict(), "result": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
