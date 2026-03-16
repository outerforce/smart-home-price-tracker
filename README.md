# 🏠 智能家居价格监控系统

自动爬取京东、天猫等平台的智能家居产品价格，监控价格变动。

## 功能特性

- 📊 多平台爬取 (京东、天猫、品牌官网)
- ⏰ 自动定时监控 (可配置间隔)
- 📈 价格趋势图表
- 🔍 产品参数展示
- 📱 简洁的 Web Dashboard

## 快速开始

### 1. 安装依赖

```bash
cd smart-home-price-tracker
pip install -r requirements.txt
```

### 2. 运行爬虫

```bash
# 一次性爬取
python main.py crawl

# 启动定时监控 (每6小时)
python main.py monitor
```

### 3. 查看数据

```bash
# 查看统计
python main.py stats

# 列出产品
python main.py list

# 打开 Dashboard
python main.py dashboard
# 或者直接在浏览器打开 dashboard/index.html
```

## 项目结构

```
smart-home-price-tracker/
├── main.py           # 主入口
├── database.py       # 数据库操作
├── crawler.py        # 爬虫模块
├── config.yaml       # 配置文件
├── requirements.txt  # Python 依赖
├── dashboard/        # 前端页面
│   ├── index.html
│   ├── products.html
│   ├── price_history.html
│   └── static/style.css
└── data/             # 数据存储 (自动创建)
    └── prices.db
```

## 配置

修改 `config.yaml` 自定义：

- 爬虫请求间隔
- 定时任务频率
- 监控的品牌和品类

## 注意事项

⚠️ 本工具仅供学习研究使用，请遵守网站的 robots.txt 和使用条款，不要频繁爬取。
