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
    get_saved_report,
    get_active_sessions,
    get_session_questions,
    mark_session_completed
)
from prompts.report import report_prompt
from datetime import datetime, time
from typing import List, Dict

logger = logging.getLogger(__name__)

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
        logger.info(f"Generating report for session {session_id}, user {user_id}")
        
        # 1. 세션 데이터 조회
        session_data = get_session_summary(session_id)
        if not session_data:
            logger.error(f"No session data found for session {session_id}")
            raise HTTPException(
                status_code=404,
                detail="세션을 찾을 수 없습니다."
            )
        
        # 2. 세션의 주제 조회
        topic = get_session_topic(session_id)
        if not topic:
            logger.error(f"No topic found for session {session_id}")
            raise HTTPException(
                status_code=404,
                detail="세션 주제를 찾을 수 없습니다."
            )
        
        # 3. 리포트 생성
        try:
            response = report_chain.invoke({
                "conversation_data": json.dumps(session_data, ensure_ascii=False)
            })
            
            # 응답 내용 로깅
            logger.debug(f"Report chain response: {response.content}")
            
            # 응답이 비어있는지 확인
            if not response.content or response.content.strip() == "":
                raise ValueError("Empty response from report chain")
                
            report = json.loads(response.content)
            logger.info(f"Generated report content for session {session_id}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from report chain: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="리포트 생성 중 잘못된 응답이 반환되었습니다."
            )
        except ValueError as e:
            logger.error(f"Invalid response from report chain: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="리포트 생성 중 오류가 발생했습니다."
            )
        except Exception as e:
            logger.error(f"Error generating report content: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="리포트 생성 중 오류가 발생했습니다."
            )
        
        # 4. 리포트 저장
        try:
            report_id = save_report(session_id, user_id, topic, report)
            logger.info(f"Saved report {report_id} for session {session_id}")
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="리포트 저장 중 오류가 발생했습니다."
            )
        
        return {
            "report_id": report_id,
            "session_id": session_id,
            "report": report
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_report_service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"리포트 생성 중 오류가 발생했습니다: {str(e)}"
        )

async def get_report_service(session_id: str) -> dict:
    try:
        logger.info(f"Retrieving report for session {session_id}")
        
        report = get_saved_report(session_id)
        if not report:
            logger.error(f"No report found for session {session_id}")
            raise HTTPException(
                status_code=404,
                detail="리포트를 찾을 수 없습니다."
            )
        
        # 리포트를 텍스트 형식으로 변환
        try:
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
            logger.info(f"Successfully formatted report for session {session_id}")
        except Exception as e:
            logger.error(f"Error formatting report: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="리포트 포맷팅 중 오류가 발생했습니다."
            )
        
        return {
            "session_id": session_id,
            "topic": report['topic'],
            "formatted_report": formatted_report,
            "raw_data": report  # 원본 데이터도 함께 반환
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_report_service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"리포트 조회 중 오류가 발생했습니다: {str(e)}"
        )

def is_midnight() -> bool:
    """현재 시간이 자정인지 확인"""
    try:
        current_time = datetime.now().time()
        return current_time.hour == 0 and current_time.minute == 0
    except Exception as e:
        logger.error(f"Error checking midnight: {str(e)}")
        return False

def is_session_completed(questions: List[Dict]) -> bool:
    """세션이 6단계까지 완료되었는지 확인"""
    try:
        if not questions:
            logger.warning("No questions found for session")
            return False
        
        # 마지막 질문의 bloom_level이 6이고 answered인지 확인
        last_question = questions[-1]
        is_completed = last_question["bloom_level"] == 6 and last_question["is_answered"]
        logger.info(f"Session completion check: {is_completed}")
        return is_completed
    except Exception as e:
        logger.error(f"Error checking session completion: {str(e)}")
        return False

async def generate_report_for_session(session_id: str, user_id: str) -> Dict:
    """특정 세션에 대한 리포트 생성"""
    try:
        logger.info(f"Generating report for session {session_id}, user {user_id}")
        
        # 1. 세션의 모든 질문과 답변 가져오기
        questions = get_session_questions(session_id)
        if not questions:
            logger.error(f"No questions found for session {session_id}")
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

        # 2. 대화 데이터 구성
        conversation_data = {
            "topic": questions[0]["topic"],
            "questions_and_answers": [
                {
                    "level": q["bloom_level"],
                    "question": q["question"],
                    "answer": q["user_answer"] if q["is_answered"] else "미응답"
                }
                for q in questions
            ]
        }

        # 3. 리포트 생성
        try:
            report_response = report_chain.invoke({
                "conversation_data": json.dumps(conversation_data, ensure_ascii=False)
            }).content
            
            try:
                report = json.loads(report_response)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response from report_chain: {report_response}")
                raise HTTPException(
                    status_code=500,
                    detail="리포트 생성 중 오류가 발생했습니다."
                )
            
            # 4. 리포트 저장
            report_id = save_report(
                session_id=session_id,
                user_id=user_id,
                topic=conversation_data["topic"],
                report=report
            )
            logger.info(f"Saved report {report_id} for session {session_id}")
            
            # 5. 세션 완료 처리
            mark_session_completed(session_id)
            logger.info(f"Marked session {session_id} as completed")
            
            return {
                "report_id": report_id,
                "session_id": session_id,
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="리포트 생성 중 오류가 발생했습니다."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_report_for_session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"리포트 생성 중 오류가 발생했습니다: {str(e)}"
        )

async def check_and_generate_reports():
    """자정이거나 6단계 완료된 세션에 대해 리포트 생성"""
    try:
        logger.info("Starting check_and_generate_reports")
        
        # 활성 세션 가져오기
        active_sessions = get_active_sessions()
        logger.info(f"Found {len(active_sessions)} active sessions")
        
        for session in active_sessions:
            session_id = session["session_id"]
            questions = get_session_questions(session_id)
            
            if is_midnight():
                # 자정인 경우 모든 활성 세션을 완료 처리하고 리포트 생성
                try:
                    mark_session_completed(session_id)
                    await generate_report_for_session(session_id, questions[0]["user_id"])
                    logger.info(f"Generated report for session {session_id} at midnight")
                except Exception as e:
                    logger.error(f"Error processing session {session_id} at midnight: {str(e)}")
            elif is_session_completed(questions):
                # 6단계 완료된 경우 리포트 생성
                try:
                    await generate_report_for_session(session_id, questions[0]["user_id"])
                    logger.info(f"Generated report for completed session {session_id}")
                except Exception as e:
                    logger.error(f"Error processing completed session {session_id}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in check_and_generate_reports: {str(e)}", exc_info=True) 