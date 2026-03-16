"""
智能家居价格爬虫 - 默认使用示例数据
需要真实数据时请确保已安装 requests: pip install requests
"""
import random
import hashlib
from datetime import datetime


# 示例产品数据 - 真实产品信息
SAMPLE_PRODUCTS = [
    # 扫地机器人
    {"brand": "科沃斯", "name": "科沃斯T20 PRO 扫拖一体机器人", "category": "扫地机器人", "price": 3999, "specs": {"吸力": "6000Pa", "续航": "180分钟", "导航": "激光导航"}},
    {"brand": "石头", "name": "石头G10S Pro 自动集尘扫拖机器人", "category": "扫地机器人", "price": 3499, "specs": {"吸力": "5100Pa", "续航": "150分钟", "导航": "激光导航"}},
    {"brand": "小米", "name": "小米扫地机器人2代", "category": "扫地机器人", "price": 1999, "specs": {"吸力": "4000Pa", "续航": "110分钟", "导航": "激光导航"}},
    {"brand": "追觅", "name": "追觅S20 Pro 扫拖机器人", "category": "扫地机器人", "price": 4299, "specs": {"吸力": "6000Pa", "续航": "180分钟", "导航": "AI视觉"}},
    {"brand": "云鲸", "name": "云鲸J3小鲸灵扫拖一体机", "category": "扫地机器人", "price": 3699, "specs": {"吸力": "3000Pa", "续航": "120分钟", "导航": "激光导航"}},
    {"brand": "美的", "name": "美的扫地机器人V10", "category": "扫地机器人", "price": 2499, "specs": {"吸力": "5000Pa", "续航": "140分钟", "导航": "激光导航"}},
    {"brand": "海尔", "name": "海尔扫地机器人TAB-T550", "category": "扫地机器人", "price": 1799, "specs": {"吸力": "3200Pa", "续航": "100分钟", "导航": "陀螺仪"}},
    
    # 空调
    {"brand": "格力", "name": "格力1.5匹变频空调挂机", "category": "空调", "price": 2699, "specs": {"匹数": "1.5匹", "能效": "一级能效", "变频": "是"}},
    {"brand": "美的", "name": "美的酷省电1.5匹空调", "category": "空调", "price": 2499, "specs": {"匹数": "1.5匹", "能效": "一级能效", "变频": "是"}},
    {"brand": "海尔", "name": "海尔1.5匹变频空调", "category": "空调", "price": 2299, "specs": {"匹数": "1.5匹", "能效": "一级能效", "变频": "是"}},
    {"brand": "小米", "name": "小米米家1.5匹空调", "category": "空调", "price": 1999, "specs": {"匹数": "1.5匹", "能效": "一级能效", "变频": "是"}},
    {"brand": "奥克斯", "name": "奥克斯1.5匹变频空调", "category": "空调", "price": 1899, "specs": {"匹数": "1.5匹", "能效": "三级能效", "变频": "是"}},
    
    # 洗衣机
    {"brand": "海尔", "name": "海尔10公斤滚筒洗衣机", "category": "洗衣机", "price": 2499, "specs": {"容量": "10公斤", "类型": "滚筒", "电机": "变频"}},
    {"brand": "小天鹅", "name": "小天鹅10公斤滚筒洗衣机", "category": "洗衣机", "price": 2299, "specs": {"容量": "10公斤", "类型": "滚筒", "电机": "变频"}},
    {"brand": "西门子", "name": "西门子10公斤滚筒洗衣机", "category": "洗衣机", "price": 3999, "specs": {"容量": "10公斤", "类型": "滚筒", "电机": "变频"}},
    {"brand": "美的", "name": "美的10公斤波轮洗衣机", "category": "洗衣机", "price": 1299, "specs": {"容量": "10公斤", "类型": "波轮", "电机": "定频"}},
    {"brand": "LG", "name": "LG 9公斤滚筒洗衣机", "category": "洗衣机", "price": 3499, "specs": {"容量": "9公斤", "类型": "滚筒", "电机": "变频"}},
    
    # 烘干机
    {"brand": "海尔", "name": "海尔10公斤热泵烘干机", "category": "烘干机", "price": 3999, "specs": {"容量": "10公斤", "类型": "热泵", "烘干": "烘干"}},
    {"brand": "小天鹅", "name": "小天鹅10公斤热泵烘干机", "category": "烘干机", "price": 3699, "specs": {"容量": "10公斤", "类型": "热泵", "烘干": "烘干"}},
    {"brand": "西门子", "name": "西门子9公斤热泵烘干机", "category": "烘干机", "price": 5999, "specs": {"容量": "9公斤", "类型": "热泵", "烘干": "烘干"}},
    
    # 智能门锁
    {"brand": "小米", "name": "小米智能门锁E10", "category": "智能门锁", "price": 799, "specs": {"开锁方式": "指纹/密码/NFC", "锁芯": "C级", "供电": "锂电池"}},
    {"brand": "德施曼", "name": "德施曼Q5M Pro智能门锁", "category": "智能门锁", "price": 1999, "specs": {"开锁方式": "指纹/密码/APP", "锁芯": "C级", "供电": "锂电池"}},
    {"brand": "凯迪仕", "name": "凯迪仕K20 Pro智能门锁", "category": "智能门锁", "price": 2299, "specs": {"开锁方式": "指纹/密码/人脸", "锁芯": "C级", "供电": "锂电池"}},
    {"brand": "鹿客", "name": "鹿客S50M Pro智能门锁", "category": "智能门锁", "price": 1799, "specs": {"开锁方式": "指纹/密码/NFC", "锁芯": "C级", "供电": "锂电池"}},
    
    # 智能音箱
    {"brand": "小米", "name": "小米小爱同学Pro", "category": "智能音箱", "price": 299, "specs": {"麦克风": "6阵列", "扬声器": "2.25寸", "屏幕": "无"}},
    {"brand": "小度", "name": "小度智能屏X10", "category": "智能音箱", "price": 899, "specs": {"麦克风": "4阵列", "屏幕": "10.1寸", "生态": "百度"}},
    {"brand": "天猫精灵", "name": "天猫精灵CC10", "category": "智能音箱", "price": 499, "specs": {"麦克风": "4阵列", "屏幕": "10.1寸", "生态": "阿里"}},
    {"brand": "华为", "name": "华为Sound X", "category": "智能音箱", "price": 999, "specs": {"麦克风": "6阵列", "扬声器": "60W", "屏幕": "无"}},
]


def generate_sample_products():
    """生成示例产品数据"""
    products = []
    
    for i, p in enumerate(SAMPLE_PRODUCTS):
        # 添加随机价格波动 (±10%)
        price_variation = random.uniform(-0.1, 0.1)
        current_price = int(p["price"] * (1 + price_variation))
        previous_price = p["price"]
        
        product = {
            "product_id": f"sample_{i+1}_{hashlib.md5(p['name'].encode()).hexdigest()[:8]}",
            "name": p["name"],
            "brand": p["brand"],
            "category": p["category"],
            "url": f"https://example.com/product/{i+1}",
            "image_url": "",
            "price": current_price,
            "previous_price": previous_price,
            "platform": "sample",
            "specs": p.get("specs", {}),
        }
        products.append(product)
    
    return products


def get_sample_stats():
    """获取示例统计"""
    categories = {}
    for p in SAMPLE_PRODUCTS:
        cat = p["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_products": len(SAMPLE_PRODUCTS),
        "today_updates": len(SAMPLE_PRODUCTS),
        "price_changes": random.randint(3, 8),
        "by_category": categories
    }


def crawl_with_fallback():
    """
    爬取数据 - 带备用方案
    优先尝试真实爬取，失败时使用示例数据
    """
    print("尝试获取真实数据...")
    
    # 尝试导入并使用真实爬虫
    try:
        from crawler_jd import crawl_jd_union
        results = crawl_jd_union()
        
        if results and len(results) >= 3:
            print(f"✅ 成功获取 {len(results)} 个真实商品")
            return results
    except ImportError:
        print("⚠️ 未安装 requests 模块")
    except Exception as e:
        print(f"⚠️ 爬取失败: {e}")
    
    # 回退到示例数据
    print("使用示例数据...")
    results = generate_sample_products()
    print(f"✅ 生成 {len(results)} 个示例产品")
    return results


if __name__ == "__main__":
    products = crawl_with_fallback()
    for p in products[:5]:
        print(f"  {p['brand']} - {p['name'][:35]}... ¥{p['price']}")
