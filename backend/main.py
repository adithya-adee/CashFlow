from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def get_head():
    return { "Hello" : "World" }
