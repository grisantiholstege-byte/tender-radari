import requests
from bs4 import BeautifulSoup
import json
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 贵州相关搜索关键词组合
search_pairs = [
    ("贵州", "包装"),
    ("贵州", "印刷"),
    ("贵州", "酒盒"),
    ("贵州", "礼盒"),
    ("贵州", "手提袋"),
    ("贵州", "出版物"),
    ("贵州", "商务印刷"),
    ("仁怀", "酒盒"),
    ("仁怀", "包装"),
    ("遵义", "包装"),
    ("贵阳", "印刷"),
    ("茅台", "包材"),
]

def fetch_bidnews():
    """从 bidnews.cn 搜索并解析"""
    items = []
    for area, kw in search_pairs:
        try:
            url = f"https://www.bidnews.cn/search?keyword={area}%20{kw}"
            r = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(r.text, 'html.parser')
            # bidnews 的搜索结果条目通常为 div.media 或 li，这里尝试通用选择器
            for block in soup.select('div.media, li.news-item'):
                title_el = block.select_one('a[href*="bidnews"]')
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                # 二次过滤关键词
                if not any(k in title for k in ['包装','印刷','酒盒','礼盒','手提袋','出版物','商务印刷','纸箱','瓶盖']):
                    continue
                href = title_el.get('href', '')
                if href and not href.startswith('http'):
                    href = 'https://www.bidnews.cn' + href
                date_span = block.select_one('span.date, small.time')
                pub_date = date_span.get_text(strip=True) if date_span else ''
                items.append({
                    "name": title,
                    "company": "（详见公告）",
                    "type": guess_type(title),
                    "pubDate": pub_date,
                    "deadline": "详见公告",
                    "status": "招标中",
                    "keyword": f"{area} {kw}",
                    "region": area if area in ['贵州','贵阳','遵义','仁怀','毕节'] else "贵州",
                    "platform": "bidnews.cn",
                    "refUrl": href
                })
            print(f"bidnews 搜索 '{area} {kw}' 抓到 {len(items)} 条（累计）")
            time.sleep(2)   # 礼貌爬取
        except Exception as e:
            print(f"bidnews 搜索 '{area} {kw}' 出错：{e}")
    return items

def fetch_qianlima():
    """从千里马招标网搜索"""
    items = []
    for area, kw in search_pairs[:6]:   # 减少请求量，只取前几个组合
        try:
            url = f"https://www.qianlima.com/search?key={area}%20{kw}"
            r = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.select('div.list_item, li.search_result_item'):
                title_el = item.select_one('a[href*="detail"]')
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if not any(k in title for k in ['包装','印刷','酒盒','礼盒','手提袋','出版物','商务印刷']):
                    continue
                href = title_el.get('href', '')
                if href and not href.startswith('http'):
                    href = 'https://www.qianlima.com' + href
                date_span = item.select_one('span.date, time')
                pub_date = date_span.get_text(strip=True) if date_span else ''
                items.append({
                    "name": title,
                    "company": "（详见公告）",
                    "type": guess_type(title),
                    "pubDate": pub_date,
                    "deadline": "详见公告",
                    "status": "招标中",
                    "keyword": f"{area} {kw}",
                    "region": area if area in ['贵州','贵阳','遵义','仁怀'] else "贵州",
                    "platform": "千里马招标网",
                    "refUrl": href
                })
            print(f"千里马搜索 '{area} {kw}' 抓到 {len(items)} 条（累计）")
            time.sleep(2)
        except Exception as e:
            print(f"千里马搜索 '{area} {kw}' 出错：{e}")
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
    all_data = []
    all_data.extend(fetch_bidnews())
    all_data.extend(fetch_qianlima())

    if not all_data:
        print("⚠️ 本次未抓取到任何项目，data.json 保持不变")
        return

    # 去重
    seen = set()
    unique = []
    for item in all_data:
        key = item['refUrl']
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"✅ 成功抓取 {len(unique)} 条招标信息")

if __name__ == '__main__':
    main()
