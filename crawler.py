import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

keywords = ['包装', '印刷', '酒盒', '礼盒', '手提袋', '出版物', '商务印刷', '纸箱', '标签', '瓶盖', '彩盒']

def fetch_bidnews():
    """从 bidnews.cn 搜索‘贵州 包装 印刷’等关键词，提取公告"""
    items = []
    search_terms = ["贵州 包装", "贵州 印刷", "贵州 酒盒", "贵州 礼盒", "贵州 手提袋", "贵州 出版物", "贵州 商务印刷"]
    for term in search_terms:
        try:
            url = f"https://www.bidnews.cn/search?keyword={term}"
            r = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(r.text, 'html.parser')
            # 根据 bidnews 搜索结果页结构解析（以实际为准，可能需要微调）
            for item in soup.select('div.search-result-item'):
                title_el = item.select_one('a.title')
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                # 二次过滤关键词
                if not any(kw in title for kw in keywords):
                    continue
                href = title_el.get('href', '')
                if href and not href.startswith('http'):
                    href = 'https://www.bidnews.cn' + href
                date_el = item.select_one('span.date')
                pub_date = date_el.get_text(strip=True) if date_el else ''
                items.append({
                    "name": title,
                    "company": "（详见公告）",
                    "type": guess_type(title),
                    "pubDate": pub_date,
                    "deadline": "详见公告",
                    "status": "招标中",
                    "keyword": "",
                    "region": "贵州",
                    "platform": "bidnews.cn",
                    "refUrl": href
                })
            print(f"搜索词‘{term}’抓取到 {len(items)} 条（累计）")
        except Exception as e:
            print(f"搜索词‘{term}’出错：{e}")
    return items

def guess_type(title):
    if any(k in title for k in ['酒盒','礼盒','手提袋','瓶盖','酒瓶']):
        return "酒类包装"
    elif any(k in title for k in ['出版物','图书','教材','报纸']):
        return "出版物印刷"
    elif any(k in title for k in ['食品','粽子','茶叶','刺梨','老干妈']):
        return "食品包装"
    elif any(k in title for k in ['商务','办公','宣传物料','表单']):
        return "商务印刷"
    else:
        return "包装印刷"

def main():
    all_data = fetch_bidnews()
    if not all_data:
        print("本次未抓取到任何项目，data.json 保持不变")
        return

    # 去重
    seen = set()
    unique = []
    for item in all_data:
        if item['refUrl'] in seen:
            continue
        seen.add(item['refUrl'])
        unique.append(item)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"✅ 成功抓取 {len(unique)} 条招标信息")

if __name__ == '__main__':
    main()
