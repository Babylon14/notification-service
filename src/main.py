from fastapi import FastAPI

from src.api.api_contacts import router as contacts_router
from src.api.api_mailings import router as mailings_router
from src.api.api_auth import router as auth_router


app = FastAPI(title="Mailing System API", version="1.0.0")

# Подключаем роутеры
app.include_router(contacts_router)
app.include_router(mailings_router)
app.include_router(auth_router)

@app.get("/", tags=["Точка входа"])
async def root():
    return {"message": "Добро пожаловать в Mailing System API"}

