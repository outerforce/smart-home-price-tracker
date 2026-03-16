"""
Slack 通知模块
"""
import json
import os
import requests
from datetime import datetime


class SlackNotifier:
    def __init__(self, webhook_url=None):
        # 从环境变量或配置文件获取 webhook URL
        self.webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")
    
    def format_products_message(self, products):
        """格式化产品列表为 Slack 消息"""
        if not products:
            return "暂无产品数据"
        
        lines = []
        for i, p in enumerate(products[:15], 1):
            # 价格变动标记
            price_str = f"¥{p.get('price', 'N/A')}"
            if p.get('previous_price'):
                diff = p.get('price', 0) - p.get('previous_price', 0)
                if diff < 0:
                    price_str += f" 📉 (降¥{abs(diff)})"
                elif diff > 0:
                    price_str += f" 📈 (+¥{diff})"
            
            name = p.get('name', 'Unknown')[:40]
            brand = p.get('brand', 'Unknown')
            
            lines.append(f"{i}. *{brand}* {name}...\n   💰 {price_str}")
        
        return "\n".join(lines)
    
    def send_price_update(self, products, stats):
        """发送价格更新到 Slack (Webhook 方式)"""
        if not self.webhook_url:
            print("⚠️ 未配置 Slack Webhook，跳过通知")
            return False
        
        # 构建消息
        text = f"""🏠 *智能家居价格更新*

📊 *统计概览*
• 总产品: {stats.get('total_products', 0)}
• 今日更新: {stats.get('today_updates', 0)}
• 价格变动: {stats.get('price_changes', 0)}

🔥 *热门产品*
{self.format_products_message(products)}

📁 *品类分布*
"""
        for cat, count in stats.get('by_category', {}).items():
            text += f"• {cat}: {count}\n"
        
        text += f"\n🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        payload = {"text": text}
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Slack 通知失败: {e}")
            return False
    
    def get_slack_message_blocks(self, products, stats):
        """获取 Slack Block Kit 格式的消息 (用于 OpenClaw)"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🏠 智能家居价格更新",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*📊 统计概览*\n• 总产品: {stats.get('total_products', 0)}\n• 今日更新: {stats.get('today_updates', 0)}\n• 价格变动: {stats.get('price_changes', 0)}"
                    }
                ]
            },
            {"type": "divider"}
        ]
        
        if products:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🔥 *热门产品 Top 10*"
                }
            })
            
            for p in products[:10]:
                price_str = f"¥{p.get('price', 'N/A')}"
                if p.get('previous_price'):
                    diff = p.get('price', 0) - p.get('previous_price', 0)
                    if diff < 0:
                        price_str += f" 📉"
                    elif diff > 0:
                        price_str += f" 📈"
                
                text = f"*{p.get('brand', '')}* {p.get('name', '')[:30]}...\n💰 {price_str}"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    }
                })
        
        if stats.get('by_category'):
            cat_text = "📁 *品类分布*\n"
            for cat, count in stats['by_category'].items():
                cat_text += f"• {cat}: {count}\n"
            
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": cat_text
                }
            })
        
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        })
        
        return blocks
    
    def send_simple_message(self, message):
        """发送简单消息"""
        if not self.webhook_url:
            return False
        
        payload = {"text": message}
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False


if __name__ == "__main__":
    notifier = SlackNotifier()
    print("Slack 通知模块已加载")
    print("配置方式: 设置环境变量 SLACK_WEBHOOK_URL")
