from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "NIDS & Mail Server System Running", "mode": "Zero-Trust Active"}