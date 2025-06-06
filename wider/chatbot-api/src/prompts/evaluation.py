from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import os

# Pydantic 모델 정의
class EvaluationResponse(BaseModel):
    is_appropriate: bool = Field(description="사용자의 응답이 적절한지 여부")
    feedback: str = Field(description="공감과 존중을 담은 자연스러운 피드백")
    is_looking_for_help: bool = Field(description="사용자가 도움을 요청하는지 여부")
    hint: str = Field(description="사용자의 생각을 이끌어내기 위한 친근한 힌트")

eval_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        당신은 학습자의 응답을 평가하는 전문가입니다. 
        사용자의 답변을 평가할 때, 너무 과도하게 근거와 팩트체크를 요구하지 마세요.
        그리고 너가 지금 최신 정보가 반영이 안되어 있으니깐, 정보의 최신성에 대해서는 평가하지 마.
        사용자가 자기 생각이나 의견을 개진하는 것이 가장 중요합니다.

        다음 JSON 형식으로 응답해주세요:
        {{
            "is_appropriate": true/false,
            "feedback": "피드백 내용",
            "is_looking_for_help": true/false,
            "hint": "힌트 내용"
        }}

        평가 기준:
        1. is_appropriate: 응답이 질문의 의도에 맞고, 적절한 수준의 사고력을 보여주는지 여부
        2. feedback: 공감과 존중을 담은 자연스러운 피드백
        3. is_looking_for_help: 사용자가 도움을 요청하는지 여부
        4. hint: 사용자의 생각을 이끌어내기 위한 친근한 힌트

        반드시 위 JSON 형식을 정확히 지켜주세요.
        """
    ),
    ("user", "질문: {question}\n블룸 레벨: {bloom_level}\n사용자 응답: {user_answer}")
])

# LLM 설정
llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7
)

# 체인 설정
eval_chain = eval_prompt | llm

def evaluate_response(question: str, bloom_level: int, user_answer: str) -> dict:
    """
    사용자의 응답을 평가하는 함수
    
    Args:
        question (str): 원래 질문
        bloom_level (int): 블룸의 인지적 수준 (1-6)
        user_answer (str): 사용자의 응답
        
    Returns:
        dict: 평가 결과를 포함하는 딕셔너리
    """
    try:
        # 평가 실행
        response = eval_chain.invoke({
            "question": question,
            "bloom_level": bloom_level,
            "user_answer": user_answer
        }).content
        
        # Pydantic 모델을 사용하여 응답 검증 및 변환
        evaluation = EvaluationResponse.model_validate_json(response)
        return evaluation.model_dump()
        
    except Exception as e:
        print(f"Error in evaluation: {str(e)}")
        # 에러 발생 시 기본 응답 반환
        default_response = EvaluationResponse(
            is_appropriate=False,
            feedback="응답을 평가하는 데 문제가 발생했습니다. 다시 시도해주세요.",
            is_looking_for_help=False,
            hint="이 주제에 대해 더 깊이 생각해볼 수 있을까요?"
        )
        return default_response.model_dump() 