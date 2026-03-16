"""
智能家居价格监控系统 - 主入口
"""
import argparse
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from database import Database
from crawler_brand import crawl_with_fallback, BrandCrawler
from slack_notify import SlackNotifier

def crawl_once(slack_notify=True):
    """执行一次爬取"""
    print("=" * 50)
    print("开始爬取智能家居价格...")
    print("=" * 50)
    
    try:
        # 使用新爬虫 (品牌官网 + 京东API)
        results = crawl_with_fallback()
        
        if not results:
            print("\n⚠️ 未能获取到数据，可能原因:")
            print("  1. 网络连接问题")
            print("  2. 网站反爬措施")
            print("  3. 网站结构变化")
            return []
        
        # 保存到数据库
        db = Database()
        
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
        
        # 获取统计
        stats = db.get_statistics()
        
        # 获取产品列表
        products = db.get_all_products()
        for p in products[:20]:
            latest = db.get_latest_price(p["product_id"])
            if latest:
                p["price"] = latest["price"]
        
        db.close()
        
        print(f"\n✅ 爬取完成! 共获取 {len(results)} 个商品")
        
        # 发送 Slack 通知
        if slack_notify:
            notifier = SlackNotifier()
            if notifier.webhook_url:
                notifier.send_price_update(products[:15], stats)
                print("✅ 已发送 Slack 通知")
        
        return results
        
    except Exception as e:
        print(f"爬取失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def stats():
    """显示统计信息"""
    db = Database()
    s = db.get_statistics()
    
    print("=" * 50)
    print("📊 智能家居价格监控系统 - 统计")
    print("=" * 50)
    print(f"总产品数: {s['total_products']}")
    print(f"今日更新: {s['today_updates']}")
    print(f"24小时内价格变动: {s['price_changes']}")
    print("\n按品类统计:")
    for cat, count in s.get("by_category", {}).items():
        print(f"  - {cat}: {count}")
    
    db.close()

def list_products(category=None, brand=None):
    """列出产品"""
    db = Database()
    products = db.get_all_products(category, brand)
    
    print("=" * 80)
    print(f"{'品牌':<10} {'产品名称':<40} {'现价':<10} {'平台':<10}")
    print("=" * 80)
    
    for p in products[:50]:
        latest = db.get_latest_price(p["product_id"])
        price = latest["price"] if latest else "N/A"
        platform = latest["platform"] if latest else "N/A"
        
        name = p["name"][:38] + ".." if len(p["name"]) > 40 else p["name"]
        print(f"{p['brand']:<10} {name:<40} {price:<10} {platform:<10}")
    
    print("=" * 80)
    print(f"共 {len(products)} 个产品")
    
    db.close()

def notify_slack():
    """手动触发 Slack 通知"""
    db = Database()
    stats = db.get_statistics()
    products = db.get_all_products()
    
    for p in products[:20]:
        latest = db.get_latest_price(p["product_id"])
        if latest:
            p["price"] = latest["price"]
    
    notifier = SlackNotifier()
    
    if notifier.webhook_url:
        success = notifier.send_price_update(products[:15], stats)
        if success:
            print("✅ Slack 通知已发送!")
        else:
            print("❌ Slack 通知发送失败")
    else:
        print("⚠️ 请设置 SLACK_WEBHOOK_URL 环境变量")
        print("\n消息预览:")
        print(notifier.format_products_message(products[:15]))
    
    db.close()

def main():
    parser = argparse.ArgumentParser(description="智能家居价格监控系统")
    parser.add_argument("command", choices=["crawl", "monitor", "stats", "list", "notify"])
    parser.add_argument("--category", "-c", help="筛选品类")
    parser.add_argument("--brand", "-b", help="筛选品牌")
    parser.add_argument("--no-slack", action="store_true", help="不发送 Slack 通知")
    
    args = parser.parse_args()
    
    if args.command == "crawl":
        crawl_once(slack_notify=not args.no_slack)
    elif args.command == "stats":
        stats()
    elif args.command == "list":
        list_products(args.category, args.brand)
    elif args.command == "notify":
        notify_slack()
    elif args.command == "monitor":
        print("定时监控功能开发中...")

if __name__ == "__main__":
    main()
