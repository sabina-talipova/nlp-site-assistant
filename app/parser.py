import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from sentence_transformers import SentenceTransformer
from datetime import datetime
from database import Page, SessionLocal, init_db

model = SentenceTransformer("all-MiniLM-L6-v2")
init_db()

def parse_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    sitemap = ET.fromstring(response.content)
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return [url.find('ns:loc', namespace).text for url in sitemap.findall('ns:url', namespace)]

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        text = soup.get_text(separator=' ', strip=True)
        return title, text
    except Exception as e:
        print(f"Ошибка на {url}: {e}")
        return "", ""

def scrape_and_store(sitemap_url):
    db = SessionLocal()
    urls = parse_sitemap(sitemap_url)
    for url in urls:
        print(f"→ Обрабатываю: {url}")
        title, content = extract_text_from_url(url)
        if content:
            embedding = model.encode([content])[0].tolist()
            page = Page(
                url=url,
                title=title,
                content=content,
                embedding=embedding,
                status="parsed",
                timestamp=datetime.utcnow()
            )
        else:
            page = Page(url=url, title="", content="", embedding=None, status="failed", timestamp=datetime.utcnow())
        db.merge(page)
        db.commit()
    db.close()

# Если запускаешь напрямую
if __name__ == "__main__":
    scrape_and_store("https://example.com/sitemap.xml")  # <-- замени на нужную ссылку
