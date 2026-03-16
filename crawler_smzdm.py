"""
什么值得买爬虫
直接爬取网站优惠信息
"""
import hashlib
import re
import time
import requests
from bs4 import BeautifulSoup


class SMZDMCrawler:
    """什么值得买爬虫"""
    
    BASE_URL = "https://www.smzdm.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.smzdm.com/",
            "Cookie": "http://www.smzdm.com/robots.txt",  # 遵守 robots.txt
        })
    
    def _fetch(self, url):
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")
            return None
    
    def _parse_price(self, text):
        """解析价格"""
        if not text:
            return 0
        match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
        if match:
            try:
                return float(match.group().replace(",", ""))
            except:
                return 0
        return 0
    
    def _generate_id(self, title, url):
        raw = f"{title}_{url}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]
    
    def get_home_deals(self, limit=20):
        """获取首页精选优惠"""
        products = []
        
        print("  📥 获取首页优惠...")
        html = self._fetch(self.BASE_URL)
        
        if not html:
            return products
        
        soup = BeautifulSoup(html, "html.parser")
        
        # 尝试多种选择器
        items = soup.select("div.item") or soup.select("li.item") or soup.select("div.z-module")
        
        for item in items[:limit]:
            try:
                # 标题
                title_el = item.select_one("h2 a") or item.select_one("a.title") or item.select_one(".title a")
                title = title_el.get_text(strip=True) if title_el else ""
                
                if not title:
                    continue
                
                # 链接
                url = ""
                if title_el and title_el.get("href"):
                    url = title_el.get("href")
                
                # 价格
                price_el = item.select_one("span.price") or item.select_one(".price") or item.select_one(".red")
                price = self._parse_price(price_el.get_text(strip=True)) if price_el else 0
                
                # 商城
                mall_el = item.select_one("a.mall") or item.select_one(".mall") or item.select_one(".shop")
                mall = mall_el.get_text(strip=True) if mall_el else "未知"
                
                # 分类
                category_el = item.select_one("a.tag") or item.select_one(".tag")
                category = category_el.get_text(strip=True) if category_el else "其他"
                
                if price > 0:
                    products.append({
                        "product_id": self._generate_id(title, url),
                        "name": title[:100],
                        "brand": mall,
                        "category": category,
                        "url": url,
                        "image_url": "",
                        "price": price,
                        "platform": "smzdm",
                        "specs": {}
                    })
                    
            except Exception as e:
                continue
        
        return products
    
    def search(self, keyword, limit=20):
        """搜索商品"""
        products = []
        
        # 搜索URL
        url = f"{self.BASE_URL}/search?keyword={keyword}"
        
        print(f"  🔍 搜索: {keyword}...")
        html = self._fetch(url)
        
        if not html:
            return products
        
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("div.item") or soup.select("li.item")
        
        for item in items[:limit]:
            try:
                title_el = item.select_one("h2 a") or item.select_one("a.title")
                title = title_el.get_text(strip=True) if title_el else ""
                
                if not title:
                    continue
                
                url = title_el.get("href", "") if title_el else ""
                
                price_el = item.select_one("span.price")
                price = self._parse_price(price_el.get_text()) if price_el else 0
                
                if price > 0:
                    products.append({
                        "product_id": self._generate_id(title, url),
                        "name": title[:100],
                        "brand": "未知",
                        "category": keyword,
                        "url": url,
                        "image_url": "",
                        "price": price,
                        "platform": "smzdm",
                        "specs": {}
                    })
                    
            except:
                continue
        
        return products
    
    def get_category(self, category_path, limit=20):
        """获取分类商品"""
        products = []
        
        # 分类URL
        url = f"{self.BASE_URL}/{category_path}"
        
        print(f"  📂 获取分类: {category_path}...")
        html = self._fetch(url)
        
        if not html:
            return products
        
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("div.item")[:limit]
        
        for item in items:
            try:
                title_el = item.select_one("h2 a")
                title = title_el.get_text(strip=True) if title_el else ""
                
                if not title:
                    continue
                
                url = title_el.get("href", "") if title_el else ""
                
                price_el = item.select_one("span.price")
                price = self._parse_price(price_el.get_text()) if price_el else 0
                
                if price > 0:
                    products.append({
                        "product_id": self._generate_id(title, url),
                        "name": title[:100],
                        "brand": "未知",
                        "category": category_path,
                        "url": url,
                        "image_url": "",
                        "price": price,
                        "platform": "smzdm",
                        "specs": {}
                    })
                    
            except:
                continue
        
        return products


def crawl_smzdm():
    """爬取什么值得买"""
    crawler = SMZDMCrawler()
    all_products = []
    
    print("\n📦 开始爬取什么值得买...")
    
    # 获取首页优惠
    print("[1] 首页精选")
    products = crawler.get_home_deals(30)
    all_products.extend(products)
    print(f"  ✅ 获取 {len(products)} 个")
    
    # 分类爬取
    categories = [
        "dazhejiadian",  # 家电
        "dazhe3c",       # 数码
        "dazhewangyou",  # 网购
    ]
    
    for cat in categories:
        products = crawler.get_category(cat, 20)
        all_products.extend(products)
        print(f"  ✅ {cat}: {len(products)} 个")
        time.sleep(1)  # 礼貌延迟
    
    # 关键词搜索
    keywords = ["扫地机器人", "空调", "洗衣机", "智能门锁"]
    
    for kw in keywords:
        products = crawler.search(kw, 15)
        all_products.extend(products)
        print(f"  ✅ 搜索 {kw}: {len(products)} 个")
        time.sleep(1)
    
    # 去重
    seen = set()
    unique = []
    for p in all_products:
        if p["product_id"] not in seen:
            seen.add(p["product_id"])
            unique.append(p)
    
    print(f"\n✅ 共获取 {len(unique)} 个商品")
    return unique


if __name__ == "__main__":
    products = crawl_smzdm()
    for p in products[:10]:
        print(f"  {p['name'][:40]}... ¥{p['price']}")
