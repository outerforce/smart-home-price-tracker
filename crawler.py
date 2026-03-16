"""
爬虫基类和调度器
"""
import hashlib
import time
import json
import yaml
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import requests


class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self, config):
        self.config = config
        self.delay = config.get("crawler", {}).get("delay", 3)
        self.max_retries = config.get("crawler", {}).get("max_retries", 3)
        self.timeout = config.get("crawler", {}).get("timeout", 30)
        self.user_agent = config.get("crawler", {}).get(
            "user_agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    
    def _get_headers(self):
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    
    def _fetch(self, url, retries=None):
        """带重试的请求"""
        retries = retries or self.max_retries
        
        for attempt in range(retries):
            try:
                response = requests.get(
                    url, 
                    headers=self._get_headers(), 
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response
            except Exception as e:
                print(f"请求失败 (尝试 {attempt + 1}/{retries}): {url}, 错误: {e}")
                if attempt < retries - 1:
                    time.sleep(self.delay * 2)
                else:
                    return None
        
        return None
    
    def _generate_product_id(self, url, name):
        """生成产品唯一ID"""
        raw = f"{url}_{name}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]
    
    @abstractmethod
    def crawl(self, keywords):
        """爬取产品列表 - 子类必须实现"""
        pass
    
    def _respect_delay(self):
        """遵守请求间隔"""
        time.sleep(self.delay)


class JDVacuumsCrawler(BaseCrawler):
    """京东扫地机器人爬虫"""
    
    PLATFORM = "jd"
    
    def crawl(self, keywords, category="扫地机器人"):
        """爬取京东扫地机器人"""
        products = []
        
        for keyword in keywords:
            url = f"https://search.jd.com/Search?keyword={keyword}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq={keyword}"
            
            response = self._fetch(url)
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 京东商品列表解析
            items = soup.select("li.gl-item")[:20]
            
            for item in items:
                try:
                    # 获取商品名称
                    name_elem = item.select_one(".p-name em")
                    name = name_elem.get_text(strip=True) if name_elem else ""
                    
                    # 获取商品链接
                    link_elem = item.select_one("a")
                    url = "https:" + link_elem.get("href") if link_elem else ""
                    
                    # 获取价格
                    price_elem = item.select_one(".p-price strong i")
                    price_text = price_elem.get_text(strip=True) if price_elem else "0"
                    try:
                        price = float(price_text)
                    except:
                        price = 0
                    
                    # 获取图片
                    img_elem = item.select_one("img.lazy-img")
                    image_url = "https:" + img_elem.get("data-lazy-img", "") if img_elem else ""
                    
                    if name and price > 0:
                        product_id = self._generate_product_id(url, name)
                        products.append({
                            "product_id": product_id,
                            "name": name,
                            "brand": self._extract_brand(name),
                            "category": category,
                            "url": url,
                            "image_url": image_url,
                            "price": price,
                            "platform": self.PLATFORM,
                            "specs": {}
                        })
                except Exception as e:
                    print(f"解析商品失败: {e}")
                    continue
                
                self._respect_delay()
        
        return products
    
    def _extract_brand(self, name):
        """从名称中提取品牌"""
        brands = ["科沃斯", "石头", "小米", "追觅", "云鲸", "美的", "海尔", "360", "松下", "iRobot"]
        for brand in brands:
            if brand in name:
                return brand
        return "其他"


class TmallCrawler(BaseCrawler):
    """天猫爬虫"""
    
    PLATFORM = "tmall"
    
    def crawl(self, keywords, category="扫地机器人"):
        """爬取天猫商品"""
        products = []
        
        for keyword in keywords:
            # 天猫搜索API
            url = f"https://s.taobao.com/search?q={keyword}&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_{time.strftime('%Y%m%d')}&ie=utf8"
            
            response = self._fetch(url)
            if not response:
                continue
            
            try:
                # 天猫搜索结果在 JavaScript 中
                text = response.text
                # 提取 JSON 数据
                import re
                match = re.search(r'g_page_config = (\{.*?\});', text, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    items = data.get("mods", {}).get("itemlist", {}).get("data", {}).get("auctions", [])[:20]
                    
                    for item in items:
                        name = item.get("title", "")
                        price = float(item.get("view_price", 0))
                        url = "https://item.taobao.com/" + item.get("nid", "")
                        image_url = "https:" + item.get("pic_url", "")
                        
                        if name and price > 0:
                            product_id = self._generate_product_id(url, name)
                            products.append({
                                "product_id": product_id,
                                "name": name,
                                "brand": self._extract_brand(name),
                                "category": category,
                                "url": url,
                                "image_url": image_url,
                                "price": price,
                                "platform": self.PLATFORM,
                                "specs": {}
                            })
            except Exception as e:
                print(f"解析天猫数据失败: {e}")
                continue
            
            self._respect_delay()
        
        return products
    
    def _extract_brand(self, name):
        """从名称中提取品牌"""
        brands = ["科沃斯", "石头", "小米", "追觅", "云鲸", "美的", "海尔", "360", "松下", "iRobot"]
        for brand in brands:
            if brand in name:
                return brand
        return "其他"


class BrandCrawler(BaseCrawler):
    """品牌官网爬虫"""
    
    BRAND_URLS = {
        "ecovacs": {
            "name": "科沃斯",
            "url": "https://www.ecovacs.com.cn/products/robot-vacuum",
            "category": "扫地机器人"
        },
        "roborock": {
            "name": "石头",
            "url": "https://www.roborock.com/products",
            "category": "扫地机器人"
        },
        "mijia": {
            "name": "小米",
            "url": "https://www.mi.com/category/robot-vacuum",
            "category": "扫地机器人"
        }
    }
    
    def crawl(self, keywords):
        """爬取品牌官网"""
        products = []
        
        for brand_key, brand_info in self.BRAND_URLS.items():
            response = self._fetch(brand_info["url"])
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 官网结构各异，这里做通用解析
            # 实际使用时需要针对每个品牌定制解析逻辑
            items = soup.select("div.product-item, li.product, div.product-card")[:10]
            
            for item in items:
                try:
                    name_elem = item.select_one("h3, .title, .product-name")
                    name = name_elem.get_text(strip=True) if name_elem else ""
                    
                    price_elem = item.select_one(".price, .sale-price, [class*='price']")
                    price_text = price_elem.get_text(strip=True) if price_elem else "0"
                    import re
                    price_match = re.search(r"[\d.]+", price_text.replace(",", ""))
                    price = float(price_match.group()) if price_match else 0
                    
                    if name and price > 0:
                        product_id = self._generate_product_id(brand_info["url"], name)
                        products.append({
                            "product_id": product_id,
                            "name": name,
                            "brand": brand_info["name"],
                            "category": brand_info["category"],
                            "url": brand_info["url"],
                            "image_url": "",
                            "price": price,
                            "platform": brand_key,
                            "specs": {}
                        })
                except Exception as e:
                    continue
            
            self._respect_delay()
        
        return products


class SuningCrawler(BaseCrawler):
    """苏宁易购爬虫"""
    
    PLATFORM = "suning"
    
    def crawl(self, keywords, category="扫地机器人"):
        """爬取苏宁易购商品"""
        products = []
        
        for keyword in keywords:
            # 苏宁搜索API
            url = f"https://search.suning.com/{keyword}/"
            
            response = self._fetch(url)
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 苏宁商品列表解析
            items = soup.select("div.item-wrap")[:20]
            
            for item in items:
                try:
                    # 获取商品名称
                    name_elem = item.select_one("div.title-wrap a")
                    name = name_elem.get("title", "") or name_elem.get_text(strip=True) if name_elem else ""
                    
                    # 获取商品链接
                    link_elem = item.select_one("div.title-wrap a")
                    url = "https://www.suning.com" + link_elem.get("href", "") if link_elem else ""
                    
                    # 获取价格
                    price_elem = item.select_one("div.def-price span")
                    price_text = price_elem.get_text(strip=True) if price_elem else "0"
                    import re
                    price_match = re.search(r"[\d.]+", price_text)
                    price = float(price_match.group()) if price_match else 0
                    
                    # 获取图片
                    img_elem = item.select_one("img")
                    image_url = img_elem.get("src", "") if img_elem else ""
                    if image_url and not image_url.startswith("http"):
                        image_url = "https:" + image_url
                    
                    if name and price > 0:
                        product_id = self._generate_product_id(url, name)
                        products.append({
                            "product_id": product_id,
                            "name": name,
                            "brand": self._extract_brand(name),
                            "category": category,
                            "url": url,
                            "image_url": image_url,
                            "price": price,
                            "platform": self.PLATFORM,
                            "specs": {}
                        })
                except Exception as e:
                    continue
                
                self._respect_delay()
        
        return products
    
    def _extract_brand(self, name):
        """从名称中提取品牌"""
        brands = ["科沃斯", "石头", "小米", "追觅", "云鲸", "美的", "海尔", "360", "松下", "iRobot", "斐纳", "戴森"]
        for brand in brands:
            if brand in name:
                return brand
        return "其他"


class CrawlerScheduler:
    """爬虫调度器"""
    
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        self.crawlers = {
            "jd": JDVacuumsCrawler(self.config),
            "tmall": TmallCrawler(self.config),
            "suning": SuningCrawler(self.config),
            "brands": BrandCrawler(self.config)
        }
    
    def crawl_all(self, db):
        """运行所有爬虫"""
        categories = self.config.get("categories", [])
        
        results = []
        
        # 按品类分别爬取
        for cat in categories:
            category_name = cat["name"]
            brands = cat.get("brands", [])
            # 品类名作为关键词
            keywords = brands + [category_name]
            
            print(f"\n📦 正在爬取: {category_name}")
            
            # 京东爬虫
            print(f"  - 京东...")
            jd_products = self.crawlers["jd"].crawl(keywords, category_name)
            results.extend(jd_products)
            
            # 天猫爬虫
            print(f"  - 天猫...")
            tmall_products = self.crawlers["tmall"].crawl(keywords, category_name)
            results.extend(tmall_products)
            
            # 苏宁易购爬虫
            print(f"  - 苏宁...")
            suning_products = self.crawlers["suning"].crawl(keywords, category_name)
            results.extend(suning_products)
            
            print(f"  {category_name}: 获取 {len(jd_products) + len(tmall_products) + len(suning_products)} 个商品")
        
        # 保存到数据库
        print("\n正在保存数据...")
        for product in results:
            db.upsert_product(
                product["product_id"],
                product["name"],
                product["brand"],
                product["category"],
                product["url"],
                product["image_url"],
                product["specs"]
            )
            db.insert_price(
                product["product_id"],
                product["price"],
                product["platform"]
            )
        
        print(f"\n✅ 完成! 共获取 {len(results)} 个商品")
        return results


if __name__ == "__main__":
    # 测试爬虫
    scheduler = CrawlerScheduler()
    print("爬虫初始化完成")
