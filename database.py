"""
数据库操作模块
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import yaml


class Database:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        db_path = config.get("database", {}).get("path", "data/prices.db")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_tables()
    
    def init_tables(self):
        """初始化数据表"""
        cursor = self.conn.cursor()
        
        # 产品表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                brand TEXT,
                category TEXT,
                url TEXT,
                image_url TEXT,
                specs TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 价格历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                price REAL NOT NULL,
                platform TEXT,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_history_product 
            ON price_history(product_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_history_date 
            ON price_history(recorded_at)
        """)
        
        self.conn.commit()
    
    def upsert_product(self, product_id, name, brand, category, url, image_url, specs):
        """插入或更新产品"""
        cursor = self.conn.cursor()
        specs_json = json.dumps(specs, ensure_ascii=False) if specs else None
        
        cursor.execute("""
            INSERT INTO products (product_id, name, brand, category, url, image_url, specs, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                name = excluded.name,
                brand = excluded.brand,
                category = excluded.category,
                url = excluded.url,
                image_url = excluded.image_url,
                specs = excluded.specs,
                updated_at = excluded.updated_at
        """, (product_id, name, brand, category, url, image_url, specs_json, datetime.now()))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def insert_price(self, product_id, price, platform):
        """插入价格记录"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO price_history (product_id, price, platform, recorded_at)
            VALUES (?, ?, ?, ?)
        """, (product_id, price, platform, datetime.now()))
        self.conn.commit()
    
    def get_all_products(self, category=None, brand=None):
        """获取所有产品"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        if brand:
            query += " AND brand = ?"
            params.append(brand)
        
        query += " ORDER BY updated_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        products = []
        for row in rows:
            product = dict(row)
            if product.get("specs"):
                product["specs"] = json.loads(product["specs"])
            products.append(product)
        
        return products
    
    def get_latest_price(self, product_id):
        """获取产品最新价格"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM price_history 
            WHERE product_id = ? 
            ORDER BY recorded_at DESC 
            LIMIT 1
        """, (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_price_history(self, product_id, days=30):
        """获取价格历史"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM price_history 
            WHERE product_id = ? 
            AND recorded_at >= datetime('now', '-' || ? || ' days')
            ORDER BY recorded_at ASC
        """, (product_id, days))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_price_changes(self, hours=24):
        """获取最近价格变动"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                ph1.product_id,
                p.name,
                p.brand,
                p.category,
                ph1.price as current_price,
                ph2.price as previous_price,
                ph1.recorded_at
            FROM price_history ph1
            JOIN products p ON ph1.product_id = p.product_id
            JOIN (
                SELECT product_id, MAX(recorded_at) as max_date
                FROM price_history
                WHERE recorded_at >= datetime('now', '-' || ? || ' hours')
                GROUP BY product_id
            ) latest ON ph1.product_id = latest.product_id AND ph1.recorded_at = latest.max_date
            LEFT JOIN price_history ph2 ON ph1.product_id = ph2.product_id 
                AND ph2.recorded_at < ph1.recorded_at
            WHERE ph2.price IS NULL OR ph1.price != ph2.price
            ORDER BY ph1.recorded_at DESC
        """, (hours,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self):
        """获取统计数据"""
        cursor = self.conn.cursor()
        
        # 总产品数
        cursor.execute("SELECT COUNT(*) as total FROM products")
        total_products = cursor.fetchone()["total"]
        
        # 今日更新数
        cursor.execute("""
            SELECT COUNT(DISTINCT product_id) as today_updates 
            FROM price_history 
            WHERE date(recorded_at) = date('now')
        """)
        today_updates = cursor.fetchone()["today_updates"]
        
        # 最近价格变动数
        cursor.execute("""
            SELECT COUNT(*) as changes 
            FROM price_history 
            WHERE recorded_at >= datetime('now', '-24 hours')
        """)
        price_changes = cursor.fetchone()["changes"]
        
        # 按品类统计
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM products 
            GROUP BY category
        """)
        by_category = {row["category"]: row["count"] for row in cursor.fetchall()}
        
        return {
            "total_products": total_products,
            "today_updates": today_updates,
            "price_changes": price_changes,
            "by_category": by_category
        }
    
    def close(self):
        """关闭连接"""
        self.conn.close()


if __name__ == "__main__":
    # 测试数据库
    db = Database()
    print("数据库初始化完成")
    print(db.get_statistics())
    db.close()
