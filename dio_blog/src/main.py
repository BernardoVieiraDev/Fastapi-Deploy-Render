
from contextlib import asynccontextmanager

from controllers import post, auth
from database import database, engine, metadata
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    from models.post import posts  # noqa
    await database.connect()
    metadata.create_all(engine)
    yield
    await database.disconnect()



app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(post.router)

# Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
