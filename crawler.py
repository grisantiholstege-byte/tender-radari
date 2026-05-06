import requests
import json
import re
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

keywords = ['包装', '印刷', '酒盒', '礼盒', '手提袋', '出版物', '商务印刷', '纸箱', '标签', '瓶盖', '彩盒']

def fetch_guizhou_api(page=1, page_size=20):
    """直接调取贵州省招标投标公共服务平台的分页接口"""
    url = "http://ztb.guizhou.gov.cn/api/bulletin/list"
    params = {
        "pageNo": page,
        "pageSize": page_size,
        "bulletinType": "1",       # 招标公告
        "keyword": ""              # 可以尝试填入关键词，但为空时我们自行筛选
    }
    items = []
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"请求失败，状态码：{r.status_code}")
            return items
        data = r.json()
        records = data.get("data", {}).get("rows", [])
        for row in records:
            title = row.get("title", "")
            # 检查标题是否包含关键词
            if not any(kw in title for kw in keywords):
                continue
            pub_date = row.get("publishDate", "")
            deadline = row.get("bidDeadline", "详见公告")
            href = row.get("url", "")
            if href and not href.startswith("http"):
                href = "http://ztb.guizhou.gov.cn" + href
            items.append({
                "name": title,
                "company": row.get("tendererName", "（详见公告）"),
                "type": guess_type(title),
                "pubDate": pub_date[:10] if pub_date else "",
                "deadline": deadline[:10] if deadline else "详见公告",
                "status": "招标中" if "结束" not in row.get("status", "") else "已结束",
                "keyword": "",
                "region": "贵州",
                "platform": "贵州招标投标公共服务平台",
                "refUrl": href
            })
        print(f"贵州平台API抓取到 {len(items)} 条")
    except Exception as e:
        print("贵州平台API抓取出错：", e)
    return items

def fetch_qianyun():
    """黔云招采（简单解析，若有变化可类似改用接口）"""
    items = []
    try:
        url = "https://www.e-qyzc.com/trade/bulletin/?pageNo=1&pageSize=20"
        r = requests.get(url, headers=headers, timeout=15)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        for li in soup.select('ul.news-list li'):
            title_el = li.select_one('a.title')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not any(kw in title for kw in keywords):
                continue
            date_el = li.select_one('span.date')
            pub_date = date_el.get_text(strip=True) if date_el else ''
            href = title_el.get('href', '')
            if href and not href.startswith('http'):
                href = 'https://www.e-qyzc.com' + href
            items.append({
                "name": title,
                "company": "（详见公告）",
                "type": guess_type(title),
                "pubDate": pub_date,
                "deadline": "详见公告",
                "status": "招标中",
                "keyword": "",
                "region": "贵州",
                "platform": "黔云招采",
                "refUrl": href
            })
        print(f"黔云招采抓取到 {len(items)} 条")
    except Exception as e:
        print("黔云招采抓取出错：", e)
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
    all_data.extend(fetch_guizhou_api(1, 20))   # 第1页
    all_data.extend(fetch_guizhou_api(2, 20))   # 第2页（可选）
    all_data.extend(fetch_qianyun())

    if not all_data:
        print("本次未抓取到任何项目，data.json保持不变")
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
