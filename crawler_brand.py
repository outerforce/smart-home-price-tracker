"""
智能家居价格爬虫 - 品牌官网版
专注于从品牌官网获取价格，更稳定可靠
"""
import hashlib
import time
import re
import json
import yaml
from bs4 import BeautifulSoup
import requests
from database import Database


class BrandCrawler:
    """品牌官网爬虫 - 更稳定的数据源"""
    
    # 品牌官网配置
    BRANDS = {
        # 扫地机器人
        "ecovacs": {
            "name": "科沃斯",
            "category": "扫地机器人",
            "products_url": "https://www.ecovacs.com.cn/collections/robot-vacuum",
            "list_selector": "div.product-item, div.product-card, li.product",
            "name_selector": "h3.product-title, h3.title, a.product-link",
            "price_selector": "span.price, div.price-box, span.sale-price",
            "specs": {
                "吸力": ["Pa", "AW"],
                "续航": ["分钟", "min"],
                "导航": ["激光", "LDS", "视觉", "陀螺仪"],
            }
        },
        "roborock": {
            "name": "石头",
            "category": "扫地机器人",
            "products_url": "https://www.roborock.com/collections/robot-vacuum",
            "list_selector": "div.product-item, div.product-card",
            "name_selector": "h3.product-title, h4.product-name",
            "price_selector": "span.price, div.price",
        },
        "mijia": {
            "name": "小米",
            "category": "扫地机器人",
            "products_url": "https://www.mi.com/shop/buy/robot",
            "list_selector": "div.product-card, li.product-item",
            "name_selector": "h3.title, div.product-name",
            "price_selector": "span.price, div.price",
        },
        "dreame": {
            "name": "追觅",
            "category": "扫地机器人",
            "products_url": "https://www.dreame.tech/collections/robot-vacuum",
            "list_selector": "div.product-item, div.product-card",
            "name_selector": "h3.product-title",
            "price_selector": "span.price",
        },
        "narwal": {
            "name": "云鲸",
            "category": "扫地机器人",
            "products_url": "https://www.narwal.com/collections/robot-vacuum",
            "list_selector": "div.product-item",
            "name_selector": "h3.product-title",
            "price_selector": "span.price",
        },
        # 空调
        "gree": {
            "name": "格力",
            "category": "空调",
            "products_url": "https://www.gree.com/products/air-conditioner",
            "list_selector": "div.product-item",
            "name_selector": "h3.product-name",
            "price_selector": "span.price",
        },
        "haier": {
            "name": "海尔",
            "category": "空调",
            "products_url": "https://www.haier.com/climate/",
            "list_selector": "div.product-item",
            "name_selector": "h3.product-name",
            "price_selector": "span.price",
        },
        # 洗衣机
        "haier_wash": {
            "name": "海尔",
            "category": "洗衣机",
            "products_url": "https://www.haier.com/laundry/",
            "list_selector": "div.product-item",
            "name_selector": "h3.product-name",
            "price_selector": "span.price",
        },
        "little_swan": {
            "name": "小天鹅",
            "category": "洗衣机",
            "products_url": "https://www.littleswan.com/products",
            "list_selector": "div.product-item",
            "name_selector": "h3.product-name",
            "price_selector": "span.price",
        },
    }
    
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        self.delay = 2
        self.timeout = 15
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
    
    def _fetch(self, url):
        """获取页面"""
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"  ❌ 获取失败: {url} - {e}")
            return None
    
    def _parse_price(self, price_text):
        """解析价格"""
        if not price_text:
            return 0
        # 提取数字
        match = re.search(r"[\d,]+\.?\d*", price_text.replace(",", ""))
        if match:
            try:
                return float(match.group().replace(",", ""))
            except:
                return 0
        return 0
    
    def _generate_id(self, name, brand):
        raw = f"{brand}_{name}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]
    
    def crawl_brand(self, brand_key, brand_info):
        """爬取单个品牌"""
        products = []
        url = brand_info.get("products_url")
        
        if not url:
            return products
        
        print(f"  🌐 爬取 {brand_info['name']}...")
        html = self._fetch(url)
        
        if not html:
            return products
        
        soup = BeautifulSoup(html, "html.parser")
        
        # 尝试多种选择器
        selectors = brand_info.get("list_selector", "div.product-item").split(", ")
        
        items = []
        for sel in selectors:
            items = soup.select(sel.strip())
            if items:
                break
        
        for item in items[:15]:  # 最多取15个
            try:
                # 产品名称
                name_selectors = brand_info.get("name_selector", "h3").split(", ")
                name = ""
                for sel in name_selectors:
                    el = item.select_one(sel.strip())
                    if el:
                        name = el.get_text(strip=True)
                        break
                
                if not name:
                    continue
                
                # 价格
                price_selectors = brand_info.get("price_selector", "span.price").split(", ")
                price = 0
                for sel in price_selectors:
                    el = item.select_one(sel.strip())
                    if el:
                        price = self._parse_price(el.get_text(strip=True))
                        break
                
                if price > 0:
                    products.append({
                        "product_id": self._generate_id(name, brand_info["name"]),
                        "name": name,
                        "brand": brand_info["name"],
                        "category": brand_info["category"],
                        "url": url,
                        "image_url": "",
                        "price": price,
                        "platform": brand_key,
                        "specs": {}
                    })
                    
            except Exception as e:
                continue
        
        print(f"    ✅ 获取 {len(products)} 个产品")
        return products
    
    def crawl_all(self):
        """爬取所有品牌"""
        all_products = []
        
        print("\n📦 开始爬取品牌官网...")
        
        for brand_key, brand_info in self.BRANDS.items():
            products = self.crawl_brand(brand_key, brand_info)
            all_products.extend(products)
            time.sleep(self.delay)  # 礼貌延迟
        
        return all_products


class JDApiCrawler:
    """京东 API 版本 - 绕过部分反爬"""
    
    PLATFORM = "jd"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.jd.com/",
        })
    
    def crawl(self, keywords, category="扫地机器人"):
        """通过搜索 API 爬取"""
        products = []
        
        for keyword in keywords:
            # 使用京东移动端 API
            url = f"https://api.m.jd.com/client.action?functionId=search&body={{\"keyword\":\"{keyword}\",\"page\":1}}"
            
            try:
                resp = self.session.get(url, timeout=10)
                data = resp.json()
                
                items = data.get("data", {}).get("searchList", {}).get("products", [])[:20]
                
                for item in items:
                    name = item.get("name", "")
                    price = item.get("price", "")
                    
                    if name and price:
                        products.append({
                            "product_id": hashlib.md5(f"{item.get('skuId')}_{name}".encode()).hexdigest()[:16],
                            "name": name[:100],
                            "brand": item.get("brandName", "其他"),
                            "category": category,
                            "url": f"https://item.jd.com/{item.get('skuId')}.html",
                            "image_url": f"https://img{item.get('imageInfo',{}).get('listImage','').replace('http://','https://')}",
                            "price": float(price) if price else 0,
                            "platform": self.PLATFORM,
                            "specs": {}
                        })
                        
            except Exception as e:
                print(f"  ❌ 京东 API 失败: {e}")
                continue
            
            time.sleep(2)
        
        return products


def crawl_with_fallback():
    """多源爬取 - 优先官网，失败则用 API"""
    print("=" * 50)
    print("开始智能家居价格爬取...")
    print("=" * 50)
    
    results = []
    
    # 1. 先尝试品牌官网
    print("\n[1/2] 爬取品牌官网...")
    brand_crawler = BrandCrawler()
    brand_products = brand_crawler.crawl_all()
    results.extend(brand_products)
    print(f"官网获取: {len(brand_products)} 个")
    
    # 2. 如果官网数据少，尝试京东 API
    if len(brand_products) < 10:
        print("\n[2/2] 尝试京东 API...")
        jd_crawler = JDApiCrawler()
        keywords = ["扫地机器人", "空调", "洗衣机", "烘干机"]
        for kw in keywords:
            jd_products = jd_crawler.crawl([kw], kw)
            results.extend(jd_products)
            print(f"  {kw}: {len(jd_products)} 个")
    
    # 去重
    seen = set()
    unique_results = []
    for p in results:
        if p["product_id"] not in seen:
            seen.add(p["product_id"])
            unique_results.append(p)
    
    print(f"\n✅ 共获取 {len(unique_results)} 个产品")
    return unique_results


if __name__ == "__main__":
    # 测试
    products = crawl_with_fallback()
    for p in products[:10]:
        print(f"  {p['brand']}: {p['name'][:30]}... ¥{p['price']}")
