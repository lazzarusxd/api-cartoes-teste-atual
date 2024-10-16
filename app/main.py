from fastapi import FastAPI
from core.configs import settings
from api.v1.api import router
from dotenv import load_dotenv


load_dotenv()
app = FastAPI(title='API - Gerenciamento de Artigos')

app.include_router(router, prefix=settings.API_V1)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level='debug', reload=True)