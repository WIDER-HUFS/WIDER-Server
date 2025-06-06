import requests
from bs4 import BeautifulSoup
import random
import datetime
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends

# 환경 설정
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

class JsonResponse(BaseModel):
    topic: str
    topic_prompt: str

# 카테고리별 헤드라인 뉴스 URL (네이버 뉴스)
CATEGORY_URLS = {
    "정치": "https://news.naver.com/section/100",
    "경제": "https://news.naver.com/section/101",
    "사회": "https://news.naver.com/section/102",
    "세계": "https://news.naver.com/section/104"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# 날짜 기준으로 오늘의 카테고리 선택
def get_today_category():
    categories = list(CATEGORY_URLS.keys())
    today = datetime.datetime.now().date()
    index = today.toordinal() % len(categories)
    return categories[index]

# 카테고리 페이지에서 헤드라인 기사 링크 수집
def get_headline_links(category_url, limit=10):
    res = requests.get(category_url, headers=HEADERS)
    soup = BeautifulSoup(res.content, 'html.parser')

    # 네이버 뉴스 헤드라인은 sa_text_title 클래스로 표시됨
    anchors = soup.select("a.sa_text_title")

    links = []
    for a in anchors:
        href = a.get("href")
        if href and href.startswith("https://n.news.naver.com/") and href not in links:
            links.append(href)
        if len(links) >= limit:
            break
    return links

# 기사 제목 + 본문 가져오기
def get_article_content(article_url):
    try:
        res = requests.get(article_url, headers=HEADERS)
        soup = BeautifulSoup(res.content, 'html.parser')
        title_tag = soup.select_one("h2#title_area span")
        content_tag = soup.select_one("div#newsct_article")

        if title_tag and content_tag:
            title = title_tag.get_text(strip=True)
            content = content_tag.get_text(separator="\n", strip=True)
            return title, content
        return None, None
    except Exception as e:
        print(f"[오류] 기사 요청 실패: {e}")
        return None, None

def extract_topic_from_articles(articles) -> dict:
    # LLM 사용해서 content에서 주제 추출
    # 예: 기본소득
    title = articles[0][0]
    content = articles[0][1]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
        당신은 뉴스 기사의 핵심 내용을 분석하여 **구체적이고 명확한 주제**와 **사고를 유도하는 질문**을 추출합니다.

        해야 할 일:
            1. 기사 내용을 읽고 **핵심 사건이나 문제**를 한 문장으로 요약.
            2. 요약을 바탕으로 **주제를 두세 단어의 명사 또는 명사구**로 표현:
                - 사회적 맥락에서 일반화 가능, 논의 여지 있는 주제.
                - 지명이나 기관명 제외.
                    - ex) 아프리카 기후 중심 경제 전환 -> 기후 중심 경제 전환
            3. **정치적 민감성**이 있다면 정당명/인명 제외, **정책 수준**이나 **사회적 현상**으로 표현.
            4. 주제 기반 **사고 유도 질문** 작성:
                - 사실 확인이 아닌 **의견/해석 요구**
                - **사회적 파급력/원인** 탐구.
            5. 결과는 아래 JSON 형식으로만 반환, 설명 제외.

        예시 출력 형식:
        {{
        "topic": "은행의 수익 구조",
        "topic_prompt": "이자 이익 중심의 은행의 수익 구조가 왜 문제가 될까요?"
        }}
        """),
    ("user", """
        기사 제목: {title}
        기사 내용: {content}
        """)
        ]
    )

    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)
    parser = JsonOutputParser(pydantic_object=JsonResponse)
    chain = prompt | llm | parser
    topic_json = chain.invoke({"title": title, "content": content})

    return topic_json # dict

def evaluate_article_suitability(articles) -> tuple:
    """
    LLM을 사용하여 기사들의 논의 적합성을 평가하고 가장 적합한 기사를 선택합니다.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        당신은 뉴스 기사의 논의 적합성을 평가하는 전문가입니다.
        다음 기준에 따라 각 기사를 평가해주세요:

        1. 사회적 영향력
           - 넓은 사회적 파급력이 있는가?
           - 많은 사람들에게 영향을 미치는가?

        2. 논의 가치
           - 다양한 관점에서 논의할 수 있는가?
           - 명확한 찬반 의견이 있을 수 있는가?

        3. 심도
           - 단순한 사실 전달이 아닌 심층적인 분석이 있는가?
           - 사회적 맥락에서 의미 있는 통찰을 제공하는가?

        4. 시의성
           - 현재 사회적 이슈와 연관이 있는가?
           - 지속적인 논의가 필요한 주제인가?

        각 기사에 대해 1-10점 사이로 점수를 매기고, 가장 높은 점수를 받은 기사의 인덱스를 반환해주세요.
        점수는 JSON 형식으로 반환해주세요.

        예시 출력:
        {{
            "scores": [8, 5, 7],
            "best_index": 0,
            "reason": "첫 번째 기사는 기본소득이라는 중요한 사회적 이슈를 다루며, 다양한 관점에서 논의할 수 있는 주제입니다."
        }}
        """),
        ("user", """
        평가할 기사들:
        {articles}
        """)
    ])

    # 기사 정보를 문자열로 변환
    articles_text = "\n\n".join([
        f"기사 {i+1}:\n제목: {title}\n내용: {content[:1000]}..." 
        for i, (title, content) in enumerate(articles)
    ])

    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    evaluation = chain.invoke({"articles": articles_text})
    return evaluation

def main():
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        category = get_today_category()
        print(f"오늘의 카테고리: {category}")

        links = get_headline_links(CATEGORY_URLS[category])
        print(f"헤드라인 기사 {len(links)}개 수집됨")

        articles = []
        min_length = 1000
        
        # 모든 기사 수집
        for link in links:
            title, content = get_article_content(link)
            if content and len(content) >= min_length:
                print(f"\n[수집된 기사]")
                print(f"제목: {title}")
                print(f"링크: {link}\n")
                articles.append((title, content))
            time.sleep(1)
        
        if len(articles) >= 3:  # 최소 3개의 기사가 수집된 경우
            # 기사 적합성 평가
            evaluation = evaluate_article_suitability(articles)
            best_index = evaluation["best_index"]
            print(f"\n[선정된 기사]")
            print(f"제목: {articles[best_index][0]}")
            print(f"선정 이유: {evaluation['reason']}")
            
            # 선정된 기사로 주제 추출
            topics = extract_topic_from_articles([articles[best_index]])
            print(f"추출된 주제: {topics}")
            return topics
        else:
            retry_count += 1
            print(f"충분한 기사를 수집하지 못했습니다. 재시도 {retry_count}/{max_retries}")
            time.sleep(2)
    
    print("모든 재시도가 실패했습니다.")
    return None

# 실행
if __name__ == "__main__":
    main()
