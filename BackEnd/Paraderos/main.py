from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/paraderos")

def obtener_paraderos():

    with open("paraderos/paraderos.json") as f:
        data = json.load(f)

    return data