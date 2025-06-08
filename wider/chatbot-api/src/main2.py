from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from api import chat, auth, report
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from services.report import check_and_generate_reports

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(report.router)

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행되는 이벤트"""
    from services.chat import check_daily_topic
    check_daily_topic()
    
    # 스케줄러 설정
    scheduler = AsyncIOScheduler()
    
    # 매일 자정에 실행
    scheduler.add_job(
        check_and_generate_reports,
        CronTrigger(hour=0, minute=0),
        id='generate_reports_at_midnight'
    )
    
    # 매 시간마다 실행 (6단계 완료된 세션 체크)
    scheduler.add_job(
        check_and_generate_reports,
        CronTrigger(minute=0),
        id='check_completed_sessions'
    )
    
    scheduler.start() 
