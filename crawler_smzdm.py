"""
什么值得买爬虫 - 修复版
使用更稳定的请求方式
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
        # 更真实的浏览器headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        })
        self.timeout = 20
    
    def _fetch(self, url):
        try:
            resp = self.session.get(url, timeout=self.timeout)
            # 检查是否被拦截
            if resp.status_code == 404 or "captcha" in resp.text.lower() or "访问频繁" in resp.text:
                print(f"  ⚠️ 被拦截或404: {url}")
                return None
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.HTTPError as e:
            print(f"  ❌ HTTP错误: {e}")
            return None
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")
            return None
    
    def _parse_price(self, text):
        if not text:
            return 0
        # 匹配各种价格格式: ¥2999, 2999元, $2999
        match = re.search(r"[$¥￥]?\s*([\d,]+\.?\d*)", text)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except:
                return 0
        return 0
    
    def _generate_id(self, title, url):
        raw = f"{title}_{url}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]
    
    def get_feng_hot(self, limit=30):
        """获取发现频道热门好价"""
        products = []
        
        # 尝试多个URL
        urls_to_try = [
            "https://www.smzdm.com/fenlei/dazhejiadian/",
            "https://www.smzdm.com/fenlei/dazhe3c/",
            "https://www.smzdm.com/fenlei/xianfenghaojia/",
        ]
        
        for url in urls_to_try:
            print(f"  📥 获取: {url}")
            html = self._fetch(url)
            
            if not html:
                continue
            
            soup = BeautifulSoup(html, "html.parser")
            
            # 尝试多种选择器
            items = soup.select("div.item")
            if not items:
                items = soup.select("li.item")
            if not items:
                items = soup.select("div.z-rank-item")
            
            for item in items[:limit]:
                try:
                    # 标题 - 尝试多种选择器
                    title = ""
                    for selector in ["h2 a", "h3 a", "a.title", ".title a", "a"]:
                        el = item.select_one(selector)
                        if el and el.get_text(strip=True):
                            title = el.get_text(strip=True)
                            break
                    
                    if not title or len(title) < 5:
                        continue
                    
                    # 获取链接
                    url = ""
                    for selector in ["h2 a", "h3 a", "a.title"]:
                        el = item.select_one(selector)
                        if el and el.get("href"):
                            url = el.get("href")
                            break
                    
                    # 价格
                    price = 0
                    for selector in ["span.price", ".price", ".red", "span.red"]:
                        el = item.select_one(selector)
                        if el:
                            price = self._parse_price(el.get_text())
                            if price > 0:
                                break
                    
                    # 商城
                    mall = "未知"
                    for selector in ["a.mall", ".mall", ".shop"]:
                        el = item.select_one(selector)
                        if el:
                            mall = el.get_text(strip=True)
                            break
                    
                    if price > 0:
                        products.append({
                            "product_id": self._generate_id(title, url),
                            "name": title[:100],
                            "brand": mall,
                            "category": "家电",
                            "url": url or "",
                            "image_url": "",
                            "price": price,
                            "platform": "smzdm",
                            "specs": {}
                        })
                        
                except Exception as e:
                    continue
            
            if products:
                break
            
            time.sleep(1)
        
        return products
    
    def search_baoyong(self, keyword, limit=20):
        """搜索什么值得买 - 使用包庸搜索接口"""
        products = []
        
        # 使用搜索API
        url = f"https://search.smzdm.com/?q={keyword}&v=1"
        
        print(f"  🔍 搜索: {keyword}")
        html = self._fetch(url)
        
        if not html:
            return products
        
        soup = BeautifulSoup(html, "html.parser")
        
        # 查找商品列表
        items = soup.select("li.item") or soup.select("div.item")
        
        for item in items[:limit]:
            try:
                title = ""
                for selector in ["h2 a", "h3 a", "a.title"]:
                    el = item.select_one(selector)
                    if el:
                        title = el.get_text(strip=True)
                        break
                
                if not title:
                    continue
                
                url = ""
                for selector in ["h2 a", "h3 a"]:
                    el = item.select_one(selector)
                    if el and el.get("href"):
                        url = el.get("href")
                        break
                
                price = 0
                for selector in ["span.price", ".price"]:
                    el = item.select_one(selector)
                    if el:
                        price = self._parse_price(el.get_text())
                        if price > 0:
                            break
                
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


def crawl_smzdm():
    """爬取什么值得买"""
    crawler = SMZDMCrawler()
    all_products = []
    
    print("\n📦 开始爬取什么值得买...")
    
    # 获取分类
    print("[1] 获取热门分类")
    products = crawler.get_feng_hot(30)
    all_products.extend(products)
    print(f"  ✅ 获取 {len(products)} 个")
    
    # 关键词搜索
    keywords = ["扫地机器人", "空调", "洗衣机", "智能门锁"]
    
    for kw in keywords:
        products = crawler.search_baoyong(kw, 15)
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
