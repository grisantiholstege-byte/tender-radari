import requests
from bs4 import BeautifulSoup
import json

def simple_fetch():
    items = []
    try:
        url = "http://ztb.guizhou.gov.cn/trade/bulletin/?pageNo=1&pageSize=5"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for li in soup.select('ul.news-list li'):
            title_el = li.select_one('a.title')
            if not title_el: continue
            title = title_el.get_text(strip=True)
            if not any(kw in title for kw in ['包装','印刷','酒盒','礼盒','手提袋','出版物','商务印刷']):
                continue
            href = title_el.get('href', '')
            if href and not href.startswith('http'):
                href = 'http://ztb.guizhou.gov.cn' + href
            items.append({
                "name": title,
                "company": "（详见公告）",
                "type": "包装印刷",
                "pubDate": "",
                "deadline": "详见公告",
                "status": "招标中",
                "keyword": "",
                "region": "贵州",
                "platform": "贵州招标投标公共服务平台",
                "refUrl": href
            })
    except Exception as e:
        print("抓取出错：", e)
    return items

if __name__ == '__main__':
    data = simple_fetch()
    if not data:
        data = [{"name":"暂无数据，请稍后刷新","company":"","type":"","pubDate":"","deadline":"","status":"","keyword":"","region":"","platform":"","refUrl":""}]
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"写入 {len(data)} 条记录")
