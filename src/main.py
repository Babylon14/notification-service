from fastapi import FastAPI
from src.api.api_contacts import router as contacts_router


app = FastAPI(title="Mailing System API", version="1.0.0")

# Подключаем роутеры
app.include_router(contacts_router)

@app.get("/", tags=["Добро пожаловать!"])
async def root():
    return {"message": "Добро пожаловать в Mailing System API"}

