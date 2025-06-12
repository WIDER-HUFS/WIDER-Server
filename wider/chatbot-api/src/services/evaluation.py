from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import os
import logging

# 로거 설정
logger = logging.getLogger(__name__)

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
        그리고 너가 지금 최신 정보가 반영이 안되어 있으니깐, 정보의 최신성에 대해서는 평가하지 마세요.
        사용자가 시사에 대한 자신의 의견을 표현하는 것이 가장 중요합니다.

        다음 JSON 형식으로 응답해주세요:
        {{
            "is_appropriate": true/false,
            "feedback": "피드백 내용",
            "is_looking_for_help": true/false,
            "hint": "힌트 내용"
        }}

        평가 기준:
         1. is_appropriate (boolean):  
           - 응답이 **질문에 명확히 반응하고**, 해당 주제에 대해 **적절한 수준의 인지적 사고**를 보여야 true입니다. 
           - 무성의하거나 불분명한 답은 답과 감정 표현, 유머, 질문 반복 요청 등도 false입니다.  
           - 답변의 길이보다는 **내용의 명확성과 관련성**이 중요합니다.

        2. feedback (string):  
           - 응답의 방향이 옳다면 칭찬하면서도 개선 방향을 제안하는 자연스럽고 공감 어린 피드백을 작성하세요. 

        3. is_looking_for_help (boolean):  
           - 사용자가 도움을 요청할 시 true입니다.  
           - 의도가 명확하지 않거나 유보적인 답변(ex: "그럴 수도 있죠", "애매하네요")도 true로 볼 수 있습니다.

        4. hint (string):  
            - 정답이 될 수 있는 정보는 주지말고, 핵심 개념을 떠올릴 수 있도록 사고를 유도하는 간접적 질문이나 맥락을 제시하세요.
            - 유도 대신 "왜 그럴까?", "무엇을 근거로 판단할 수 있을까?" 형태의 질문으로 유도하세요.
            - 질문을 보고, 질문에 맞는 맥락과 방향의 힌트를 주세요.

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
        
        # 마크다운 코드 블록 제거
        if response.startswith("```json"):
            response = response[7:]  # ```json 제거
        if response.endswith("```"):
            response = response[:-3]  # ``` 제거
        response = response.strip()
        
        # Pydantic 모델을 사용하여 응답 검증 및 변환
        evaluation = EvaluationResponse.model_validate_json(response)
        return evaluation.model_dump()
        
    except Exception as e:
        logger.error(f"Error in evaluation: {str(e)}")
        # 에러 발생 시 기본 응답 반환
        default_response = EvaluationResponse(
            is_appropriate=False,
            feedback="응답을 평가하는 데 문제가 발생했습니다. 다시 시도해주세요.",
            is_looking_for_help=False,
            hint="이 주제에 대해 더 깊이 생각해볼 수 있을까요?"
        )
        return default_response.model_dump() 