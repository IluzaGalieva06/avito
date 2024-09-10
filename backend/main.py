from fastapi import FastAPI
import models
import database
from routes import router

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
