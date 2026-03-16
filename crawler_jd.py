"""
京东联盟爬虫
使用京东联盟 API 获取商品信息
"""
import hashlib
import time
import requests
import json
import re


class JDUnionCrawler:
    """京东联盟 API 爬虫"""
    
    def __init__(self, auth_code=None):
        # 京东联盟授权码
        self.auth_code = auth_code or "6ef3fbb8dfe5d8e2cc8f0f8ad649bfa910751fa0d24f7a12622fd72191bfec5fc60d82462a4a5425"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
        })
        
        # 京东联盟 API 地址
        self.api_url = "https://api.jd.com/routerjson"
        
        # 缓存的授权信息
        self.access_token = None
    
    def _generate_sign(self, params, app_secret):
        """生成京东签名"""
        # 按参数名排序
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        # 拼接字符串
        sign_str = app_secret
        for k, v in sorted_params:
            sign_str += f"{k}{v}"
        sign_str += app_secret
        # MD5 签名
        import hashlib
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    
    def _call_api(self, method, params):
        """调用京东联盟 API"""
        # 系统参数
        system_params = {
            "app_key": "jd_union_sdk",  # 使用通用key
            "method": method,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "format": "json",
            "v": "1.0",
            "sign_method": "md5",
            "360buy_param_json": json.dumps(params, ensure_ascii=False),
        }
        
        try:
            # 尝试直接请求商品
            url = f"https://api.jd.com/routerjson?app_key=jd_union_sdk&method={method}&timestamp={system_params['timestamp']}&format=json&v=1.0&sign_method=md5"
            resp = self.session.post(url, data={"360buy_param_json": json.dumps(params)}, timeout=15)
            
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"  ❌ API调用失败: {e}")
        
        return None
    
    def search_by_keyword(self, keyword, page_index=0, page_size=20):
        """关键词搜索商品"""
        products = []
        
        # 使用京东移动端搜索 API
        url = "https://api.m.jd.com/client.action"
        
        params = {
            "functionId": "search",
            "body": json.dumps({
                "keyword": keyword,
                "pageIndex": page_index,
                "pageSize": page_size,
                "sortName": "inOrderCount",
                "sort": "desc",
            }, ensure_ascii=False),
            "client": "whale",
            "clientVersion": "13.2.3",
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://jd.com/",
        }
        
        try:
            resp = self.session.post(url, data=params, headers=headers, timeout=15)
            data = resp.json()
            
            # 解析商品列表
            search_result = data.get("data", {}).get("searchList", {})
            items = search_result.get("products", []) or search_result.get("goods", [])
            
            for item in items:
                try:
                    name = item.get("name", item.get("goodsName", ""))
                    price = item.get("price", item.get("lowestPrice", 0))
                    sku_id = item.get("skuId", item.get("sku_id", ""))
                    
                    if name and price:
                        # 提取品牌
                        brand = self._extract_brand(name)
                        
                        products.append({
                            "product_id": f"jd_{sku_id}",
                            "name": name[:100],
                            "brand": brand,
                            "category": keyword,
                            "url": f"https://item.jd.com/{sku_id}.html",
                            "image_url": item.get("imageUrl", ""),
                            "price": float(price) if price else 0,
                            "platform": "jd",
                            "specs": {}
                        })
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"  ❌ 搜索失败: {e}")
        
        return products
    
    def _extract_brand(self, name):
        """从名称提取品牌"""
        brands = [
            "科沃斯", "石头", "小米", "追觅", "云鲸", "美的", "海尔", "360",
            "格力", "奥克斯", "TCL", "大金", "三菱电机",
            "小天鹅", "西门子", "松下", "LG", "三星", "博世",
            "德施曼", "凯迪仕", "鹿客", "飞利浦", "VOC",
            "小度", "天猫精灵", "华为", "苹果"
        ]
        
        for brand in brands:
            if brand in name:
                return brand
        return "其他"
    
    def get_top_goods(self, category_id=None, limit=30):
        """获取京东热销商品"""
        products = []
        
        # 热门品类ID
        category_ids = {
            "扫地机器人": "670",
            "空调": "731",
            "洗衣机": "720",
            "烘干机": "1620",
            "智能门锁": "1684",
            "智能音箱": "652",
        }
        
        # 使用京东联盟转链接口
        for cat_name, cat_id in category_ids.items():
            print(f"  📦 获取 {cat_name}...")
            
            url = "https://api.m.jd.com/client.action"
            
            params = {
                "functionId": "hotgoods",
                "body": json.dumps({
                    "cid1": cat_id,
                    "pageIndex": 1,
                    "pageSize": 20,
                }, ensure_ascii=False),
                "client": "whale",
                "clientVersion": "13.2.3",
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            
            try:
                resp = self.session.post(url, data=params, headers=headers, timeout=15)
                data = resp.json()
                
                items = data.get("data", {}).get("hotGoods", [])
                
                for item in items[:limit]:
                    try:
                        name = item.get("name", "")
                        price = item.get("price", 0)
                        sku_id = item.get("skuId", "")
                        
                        if name and price:
                            products.append({
                                "product_id": f"jd_{sku_id}",
                                "name": name[:100],
                                "brand": self._extract_brand(name),
                                "category": cat_name,
                                "url": f"https://item.jd.com/{sku_id}.html",
                                "image_url": "",
                                "price": float(price),
                                "platform": "jd",
                                "specs": {}
                            })
                            
                    except:
                        continue
                        
            except Exception as e:
                print(f"    ❌ 获取失败: {e}")
            
            time.sleep(0.5)
        
        return products


def crawl_jd_union():
    """爬取京东联盟商品"""
    crawler = JDUnionCrawler()
    all_products = []
    
    print("\n📦 开始爬取京东商品...")
    
    # 1. 获取热门商品分类
    print("[1] 获取热销商品")
    products = crawler.get_top_goods(limit=30)
    all_products.extend(products)
    print(f"  ✅ 获取 {len(products)} 个")
    
    # 2. 关键词搜索
    keywords = ["扫地机器人", "空调 变频", "洗衣机", "烘干机", "智能门锁", "智能音箱"]
    
    for kw in keywords:
        products = crawler.search_by_keyword(kw, page_size=20)
        all_products.extend(products)
        print(f"  ✅ {kw}: {len(products)} 个")
        time.sleep(0.5)
    
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
    products = crawl_jd_union()
    for p in products[:10]:
        print(f"  {p['brand']} - {p['name'][:35]}... ¥{p['price']}")
