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

당신이 해야 할 일은 다음과 같습니다:

1. 기사 내용의 핵심 정보를 파악하여 한 문장으로 요약합니다.
2. 이 요약을 기반으로 **주제를 한 단어**로 추출합니다. 주제는 반드시 **명사**여야 하며, 너무 포괄적이거나 추상적인 단어(예: '사회', '현상')는 피해주세요.
3. 만약 기사 내용이 **특정 정치인, 정당, 국가 등 민감한 사안**을 다루고 있다면, 주제를 **정치적으로 중립적인 용어**로 일반화하거나 간접화하여 표현하세요.
4. 추출된 주제를 기반으로, 사용자의 흥미를 유도하고 사고를 유발할 수 있는 **질문**을 하나 작성하세요. 질문은 고등학생 수준의 일반 독자가 이해할 수 있도록 **직관적이고 간결하게 작성**하세요.
5. 결과는 반드시 아래 JSON 형식으로 반환하세요. 그 외의 문장은 포함하지 마세요.

예시 출력 형식:
{{
  "topic": "기후",
  "topic_prompt": "기후 변화가 우리 일상에 미치는 영향은 어떤 모습일까요?"
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
