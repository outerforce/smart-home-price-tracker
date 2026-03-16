"""
智能家居价格监控系统 - 主入口
"""
import argparse
from database import Database
from crawler import CrawlerScheduler

def crawl_once():
    print("开始爬取...")
    try:
        db = Database()
        scheduler = CrawlerScheduler()
        scheduler.crawl_all(db)
        db.close()
        print("爬取完成!")
    except Exception as e:
        print(f"爬取失败: {e}")

def stats():
    db = Database()
    s = db.get_statistics()
    print(f"总产品数: {s[\"total_products\"]}")
    print(f"今日更新: {s[\"today_updates\"]}")
    db.close()

def list_products(category=None, brand=None):
    db = Database()
    products = db.get_all_products(category, brand)
    print(f"共 {len(products)} 个产品")
    for p in products[:20]:
        latest = db.get_latest_price(p["product_id"])
        price = latest["price"] if latest else "N/A"
        print(f"{p[\"brand\"]} - {p[\"name\"][:30]} - {price}元")
    db.close()

def main():
    parser = argparse.ArgumentParser(description="智能家居价格监控系统")
    parser.add_argument("command", choices=["crawl", "stats", "list"])
    parser.add_argument("--category", "-c")
    parser.add_argument("--brand", "-b")
    args = parser.parse_args()
    if args.command == "crawl":
        crawl_once()
    elif args.command == "stats":
        stats()
    elif args.command == "list":
        list_products(args.category, args.brand)

if __name__ == "__main__":
    main()

