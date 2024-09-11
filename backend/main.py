from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
import models
import database
from routes import router

app = FastAPI()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500, content={"detail": "Сервер не готов обрабатывать запросы"}
    )


models.Base.metadata.create_all(bind=database.engine)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
