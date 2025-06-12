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
    "IT/과학": "https://news.naver.com/section/105",
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
    당신은 뉴스 기사의 핵심 내용을 분석하여, 주제와 주제 관련 질문을 추출하는 역할을 맡고 있습니다.

    작성 조건은 다음과 같습니다.
        
    - **topic**: 
    - 반드시 쟁점이나 사건을 요약한 3-4개의 단어로 이루어진 명사형 주제여야 합니다.
    - 너무 포괄적이거나 추상적인 단어(예: ‘사회’, ‘현상’)는 피하고, **시사적 쟁점**을 고려해야 합니다.

    - **topic_prompt**:
    - 이 질문은 Bloom’s Taxonomy 기반 질문 생성을 위한 **문맥(Context)** 역할을 합니다.
    - **기사 전체를 5문장 이하의 문단**으로 요약해 주세요.
    - 다음 요소들 중 시사적으로 의미있는 내용들을 꼭 포함해주세요.:
        - 무엇이 벌어졌는가? (**주요 사건**)
        - 누가 관련되어 있으며 어떤 입장을 보였는가? (**이해 당사자**)
        - 사회적·정치적으로 어떤 갈등이나 쟁점이 존재하는가? (**쟁점**)
        - 이 사건이 발생한 맥락이나 역사적 배경은 무엇인가? (**배경**)
        - 이 사안이 향후 어떤 사회적·정책적 영향을 미칠 수 있는가? (**파급 효과**)
        
    출력 형식:
    {{
    "topic": "명사형 주제",
    "topic_prompt": "기사 맥락과 쟁점을 담은 설명문"
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

# 메인 실행 함수
def main():
    max_retries = 3  # 최대 재시도 횟수
    retry_count = 0
    
    while retry_count < max_retries:
        category = get_today_category()
        print(f"오늘의 카테고리: {category}")

        links = get_headline_links(CATEGORY_URLS[category])
        print(f"헤드라인 기사 {len(links)}개 수집됨")

        random.shuffle(links)
        articles = []
        min_length = 500  # 최소 길이 조건 완화
        
        # 첫 번째 기사는 무조건 수집
        for link in links:
            title, content = get_article_content(link)
            if content and len(content) >= min_length:
                print("\n[선택된 뉴스 기사]")
                print(f"제목: {title}")
                print(f"링크: {link}\n")
                print("[본문 내용]")
                print(content)
                articles.append((title, content))
                break
            else:
                print(f"건너뜀 (길이 부족): {link}")
            time.sleep(1)
        
        # 추가 기사 수집 (articles에 기사가 없는 경우 대비하여)
        for link in links:
            if len(articles) >= 3:  # 최대 3개까지만 수집
                break
            title, content = get_article_content(link)
            if content and len(content) >= 1000:  # 추가 기사는 원래 조건 유지
                print("\n[추가 기사]")
                print(f"제목: {title}")
                print(f"링크: {link}\n")
                articles.append((title, content))
            time.sleep(1)
        
        if articles:  # 기사가 수집된 경우
            # 주제 추출
            random.shuffle(articles)
            topics = extract_topic_from_articles([articles[0]])
            print(f"추출된 주제: {topics}")
            return topics
        else:
            retry_count += 1
            print(f"기사 수집 실패. 재시도 {retry_count}/{max_retries}")
            time.sleep(2)  # 재시도 전 잠시 대기
    
    # 모든 재시도가 실패한 경우
    # print("모든 재시도가 실패했습니다. 기본 주제로 진행합니다.")
    # articles = [("기본소득", "기본소득에 대한 기사 내용입니다.")]
    # topics = extract_topic_from_articles(articles)
    print(f"추출된 주제: {topics}")
    return topics

# 실행
if __name__ == "__main__":
    main()
