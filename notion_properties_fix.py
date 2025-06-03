
def _build_page_properties(self, today, current_time, articles, keywords, summary):
    """실제 데이터베이스 스키마에 맞는 페이지 속성 구성"""
    try:
        title = f"🤖 Google News AI 리포트 - {today} {current_time}"
        
        properties = {
            "Title": {  # 실제 제목 속성명 사용
                "title": [
                    {
                        "type": "text",
                        "text": {"content": title}
                    }
                ]
            }
            "Date": {
                "date": {"start": today}
            },
            "Source Count": {
                "number": len(articles)
            },
            "Top Keywords": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": ", ".join(keywords[:10]) if keywords else "AI, Google News"}
                    }
                ]
            },
            "Category": {
                "select": {"name": "AI 뉴스"}
            },
            "Status": {
                "select": {"name": "완료"}
            },
        }
        
        return properties
        
    except Exception as e:
        logger.error(f"페이지 속성 구성 오류: {e}")
        # 최소한의 속성만 반환
        return {
            "Title": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": f"Google News AI 리포트 - {today}"}
                    }
                ]
            }
        }
