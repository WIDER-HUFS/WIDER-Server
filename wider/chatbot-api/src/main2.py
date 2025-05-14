from fastapi import FastAPI
import logging
from api import chat, report

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

# 라우터 등록
app.include_router(chat.router)
app.include_router(report.router)

@app.on_event("startup")
async def startup_event():
    from services.chat import check_daily_topic
    check_daily_topic() 
