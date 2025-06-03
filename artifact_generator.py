# artifact_generator.py - link 키 오류 수정 버전

from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ArtifactGenerator:
    """HTML 및 마크다운 리포트 생성기"""
    
    def __init__(self):
        from config import Config
        self.config = Config
    
    def generate_html_report(self, summary_data):
        """HTML 리포트 생성"""
        try:
            articles = summary_data.get('articles', [])
            top_keywords = summary_data.get('top_keywords', [])
            overall_summary = summary_data.get('summary', '')
            
            # HTML 헤더
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google News AI 리포트 - {datetime.now().strftime('%Y-%m-%d')}</title>
    {self.config.HTML_REPORT_STYLE}
</head>
<body>
    <div class="header">
        <h1>🤖 Google News AI 뉴스 리포트</h1>
        <p>📅 생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}</p>
        <p>📊 수집 기사: {len(articles)}개</p>
    </div>
    
    <div class="summary-section">
        <h2>📈 오늘의 AI 뉴스 트렌드</h2>
        <p>{overall_summary}</p>
    </div>
    
    <div class="keywords">
        <h3>🏷️ 주요 키워드</h3>
        {self._generate_keywords_html(top_keywords)}
    </div>
    
    <div class="articles-section">
        <h2>📰 주요 뉴스 ({len(articles)}개)</h2>
        {self._generate_articles_html(articles)}
    </div>
    
    <div class="footer">
        <hr>
        <p>💡 이 리포트는 Google News와 OpenAI를 활용하여 자동 생성되었습니다.</p>
        <p>🔗 시스템: {self.config.SYSTEM_NAME} {self.config.SYSTEM_VERSION}</p>
        <p>👨‍💻 개발자: {self.config.DEVELOPER_NAME}</p>
    </div>
</body>
</html>
"""
            
            print("✅ HTML 리포트 생성 완료")
            return html_content.strip()
            
        except Exception as e:
            logger.error(f"HTML 리포트 생성 실패: {e}")
            return self._generate_fallback_html(summary_data)
    
    def _generate_keywords_html(self, keywords):
        """키워드 HTML 생성"""
        if not keywords:
            return '<p>키워드 없음</p>'
        
        keywords_html = []
        for keyword in keywords[:10]:  # 최대 10개
            keywords_html.append(f'<span class="keyword">#{keyword}</span>')
        
        return ' '.join(keywords_html)
    
    def _generate_articles_html(self, articles):
        """기사 HTML 생성 - 안전한 키 접근"""
        if not articles:
            return '<p>수집된 기사가 없습니다.</p>'
        
        articles_html = []
        
        for i, article in enumerate(articles, 1):
            try:
                # 🔧 안전한 키 접근으로 수정
                title = article.get('title', '제목 없음')
                summary = article.get('summary', '요약 없음')
                url = article.get('url', '#')  # 'link' 대신 'url' 사용
                source = article.get('source', '출처 미상')
                published = article.get('published', '시간 미상')
                keywords = article.get('keywords', [])
                category = article.get('category', 'AI 뉴스')
                
                # 발행 시간 포맷팅
                if isinstance(published, datetime):
                    published_str = published.strftime('%m-%d %H:%M')
                elif isinstance(published, str):
                    published_str = published
                else:
                    published_str = '시간 미상'
                
                # 키워드 HTML
                keywords_html = ''
                if keywords:
                    keywords_list = [f'<span class="keyword">#{kw}</span>' for kw in keywords[:3]]
                    keywords_html = f'<div class="keywords">{" ".join(keywords_list)}</div>'
                
                # 기사 HTML
                article_html = f"""
                <div class="article">
                    <div class="title">
                        <a href="{url}" target="_blank" style="text-decoration: none; color: #2c3e50;">
                            {i}. {title}
                        </a>
                    </div>
                    <div class="meta">
                        📍 {source} | ⏰ {published_str} | 🏷️ {category}
                    </div>
                    <div class="summary">
                        {summary}
                    </div>
                    {keywords_html}
                </div>
                """
                
                articles_html.append(article_html)
                
            except Exception as e:
                logger.warning(f"기사 HTML 생성 실패 (#{i}): {e}")
                # 오류 발생 시 기본 HTML
                fallback_html = f"""
                <div class="article">
                    <div class="title">{i}. 기사 처리 오류</div>
                    <div class="summary">이 기사를 처리하는 중 오류가 발생했습니다.</div>
                </div>
                """
                articles_html.append(fallback_html)
        
        return '\n'.join(articles_html)
    
    def generate_markdown_report(self, summary_data):
        """마크다운 리포트 생성"""
        try:
            articles = summary_data.get('articles', [])
            top_keywords = summary_data.get('top_keywords', [])
            overall_summary = summary_data.get('summary', '')
            
            # 마크다운 헤더
            markdown_content = f"""# 🤖 Google News AI 뉴스 리포트

**📅 생성일:** {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}  
**📊 수집 기사:** {len(articles)}개  
**🔗 시스템:** {self.config.SYSTEM_NAME} {self.config.SYSTEM_VERSION}

## 📈 오늘의 AI 뉴스 트렌드

{overall_summary}

## 🏷️ 주요 키워드

{self._generate_keywords_markdown(top_keywords)}

## 📰 주요 뉴스 ({len(articles)}개)

{self._generate_articles_markdown(articles)}

---

💡 이 리포트는 Google News와 OpenAI를 활용하여 자동 생성되었습니다.  
👨‍💻 개발자: {self.config.DEVELOPER_NAME}
"""
            
            print("✅ 마크다운 리포트 생성 완료")
            return markdown_content.strip()
            
        except Exception as e:
            logger.error(f"마크다운 리포트 생성 실패: {e}")
            return f"# 리포트 생성 오류\n\n마크다운 리포트 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _generate_keywords_markdown(self, keywords):
        """키워드 마크다운 생성"""
        if not keywords:
            return '키워드 없음'
        
        keywords_md = [f"`#{keyword}`" for keyword in keywords[:10]]
        return ' '.join(keywords_md)
    
    def _generate_articles_markdown(self, articles):
        """기사 마크다운 생성 - 안전한 키 접근"""
        if not articles:
            return '수집된 기사가 없습니다.'
        
        articles_md = []
        
        for i, article in enumerate(articles, 1):
            try:
                # 🔧 안전한 키 접근으로 수정
                title = article.get('title', '제목 없음')
                summary = article.get('summary', '요약 없음')
                url = article.get('url', '#')  # 'link' 대신 'url' 사용
                source = article.get('source', '출처 미상')
                published = article.get('published', '시간 미상')
                keywords = article.get('keywords', [])
                category = article.get('category', 'AI 뉴스')
                
                # 발행 시간 포맷팅
                if isinstance(published, datetime):
                    published_str = published.strftime('%m-%d %H:%M')
                elif isinstance(published, str):
                    published_str = published
                else:
                    published_str = '시간 미상'
                
                # 키워드 마크다운
                keywords_md = ''
                if keywords:
                    keywords_list = [f"`#{kw}`" for kw in keywords[:3]]
                    keywords_md = f"\n**키워드:** {' '.join(keywords_list)}"
                
                # 기사 마크다운
                article_md = f"""### {i}. [{title}]({url})

**📍 출처:** {source} | **⏰ 발행:** {published_str} | **🏷️ 분류:** {category}

**💡 요약:** {summary}{keywords_md}

---
"""
                
                articles_md.append(article_md)
                
            except Exception as e:
                logger.warning(f"기사 마크다운 생성 실패 (#{i}): {e}")
                # 오류 발생 시 기본 마크다운
                fallback_md = f"""### {i}. 기사 처리 오류

이 기사를 처리하는 중 오류가 발생했습니다.

---
"""
                articles_md.append(fallback_md)
        
        return '\n'.join(articles_md)
    
    def _generate_fallback_html(self, summary_data):
        """오류 발생 시 기본 HTML"""
        return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>리포트 생성 오류</title>
</head>
<body>
    <h1>❌ 리포트 생성 오류</h1>
    <p>HTML 리포트 생성 중 오류가 발생했습니다.</p>
    <p>생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>수집된 기사 수: {len(summary_data.get('articles', []))}개</p>
</body>
</html>
"""

def test_generator():
    """아티팩트 생성기 테스트"""
    print("🧪 아티팩트 생성기 테스트")
    
    # 테스트 데이터
    test_data = {
        'articles': [
            {
                'title': '테스트 AI 뉴스',
                'summary': '이것은 테스트 요약입니다.',
                'url': 'https://example.com',
                'source': '테스트 뉴스',
                'published': datetime.now(),
                'keywords': ['AI', '테스트'],
                'category': 'AI 뉴스'
            }
        ],
        'top_keywords': ['AI', '인공지능', '테스트'],
        'summary': '오늘의 AI 뉴스 트렌드 테스트'
    }
    
    generator = ArtifactGenerator()
    html_content = generator.generate_html_report(test_data)
    markdown_content = generator.generate_markdown_report(test_data)
    
    print(f"✅ HTML 길이: {len(html_content)}자")
    print(f"✅ 마크다운 길이: {len(markdown_content)}자")

if __name__ == "__main__":
    test_generator()