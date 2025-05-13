import json
import asyncio
import logging
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from config.settings import OPENAI_API_KEY
from database.db import (
    get_session_summary,
    get_session_topic,
    save_report,
    get_saved_report
)
from prompts.report import report_prompt

# LLM 설정
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    request_timeout=60  # 60초 타임아웃 설정
)

# 체인 설정
report_chain = report_prompt | llm

async def generate_report_service(session_id: str, user_id: str) -> dict:
    try:
        # 1. 세션 데이터 조회
        session_data = get_session_summary(session_id)
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="세션을 찾을 수 없습니다."
            )
        
        # 2. 세션의 주제 조회
        topic = get_session_topic(session_id)
        
        # 3. 리포트 생성
        report = json.loads(
            report_chain.invoke({
                "conversation_data": json.dumps(session_data, ensure_ascii=False)
            }).content
        )
        
        # 4. 리포트 저장
        report_id = save_report(session_id, user_id, topic, report)
        
        return {
            "report_id": report_id,
            "session_id": session_id,
            "report": report
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"리포트 생성 중 오류가 발생했습니다: {str(e)}"
        )

async def get_report_service(session_id: str) -> dict:
    report = get_saved_report(session_id)
    if not report:
        raise HTTPException(
            status_code=404,
            detail="리포트를 찾을 수 없습니다."
        )
    
    # 리포트를 텍스트 형식으로 변환
    formatted_report = f"""📊 학습 리포트

📝 요약
{report['summary']}

💪 강점
"""
    
    # 강점 추가
    for strength in report['strengths']:
        formatted_report += f"""
• {strength['title']}
  - {strength['description']}
  - 예시: {strength['example']}
"""
    
    formatted_report += "\n🔍 개선점"
    # 개선점 추가
    for weakness in report['weaknesses']:
        formatted_report += f"""
• {weakness['title']}
  - {weakness['description']}
  - 제안: {weakness['suggestion']}
"""
    
    formatted_report += "\n💡 제안사항"
    # 제안사항 추가
    for suggestion in report['suggestions']:
        formatted_report += f"""
• {suggestion['title']}
  - {suggestion['description']}
  - 추천 자료: {suggestion['resources']}
  - 생각해볼 질문:
"""
        for question in suggestion['questions']:
            formatted_report += f"    - {question}\n"
    
    formatted_report += f"""
✨ 발전된 응답 예시
{report['revised_suggestion']}

📅 생성일시: {report['created_at']}
"""
    
    return {
        "session_id": session_id,
        "topic": report['topic'],
        "formatted_report": formatted_report,
        "raw_data": report  # 원본 데이터도 함께 반환
    } 