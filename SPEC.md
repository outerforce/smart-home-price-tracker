# 智能家居价格监控系统 - 规格说明书

## 1. 项目概述

**项目名称**: Smart Home Price Tracker  
**项目类型**: Python 爬虫 + 数据监控 Dashboard  
**核心功能**: 爬取主流电商/品牌官网的智能家居、扫地机器人价格，存储历史数据并可视化展示  
**目标用户**: 消费者、产品研究者、价格敏感用户

---

## 2. 技术栈

| 层级 | 技术选型 |
|------|----------|
| 爬虫 | Python + requests + BeautifulSoup4 |
| 数据存储 | SQLite (轻量级，无需额外服务) |
| 定时任务 | schedule (Python 内置) |
| 前端展示 | HTML + Chart.js (本地文件浏览器打开) |
| 部署 | Docker (可选) |

---

## 3. 数据模型

### 3.1 产品表 (products)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| product_id | TEXT | 唯一标识 (URL hash) |
| name | TEXT | 产品名称 |
| brand | TEXT | 品牌 |
| category | TEXT | 品类: 扫地机器人/智能音箱/智能门锁/空调/扫地机器人配件 |
| url | TEXT | 产品链接 |
| image_url | TEXT | 产品图片 |
| specs | TEXT | 参数 JSON (JSON 格式存储) |
| created_at | DATETIME | 首次发现时间 |
| updated_at | DATETIME | 最后更新 |

### 3.2 价格历史表 (price_history)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| product_id | TEXT | 外键 -> products.product_id |
| price | REAL | 价格 (元) |
| platform | TEXT | 来源平台: jd/tmall/baidu/ecovacs/roborock/mijia |
| recorded_at | DATETIME | 记录时间 |

---

## 4. 功能模块

### 4.1 爬虫模块 (crawlers/)

```
crawlers/
├── base.py          # 基类，定义爬取接口
├── jd_crawler.py    # 京东爬虫
├── tmall_crawler.py # 天猫爬虫
├── baidu_crawler.py # 百度电商
├── ecovacs_crawler.py # 科沃斯官网
├── roborock_crawler.py # 石头科技官网
└── mijia_crawler.py # 小米米家
```

**爬取策略**:
- 遵守 robots.txt
- 添加合理请求间隔 (2-3 秒)
- 模拟正常浏览器 User-Agent
- 失败重试最多 3 次

### 4.2 数据存储模块 (database.py)

- SQLite 连接管理
- 初始化表结构
- CRUD 操作封装

### 4.3 定时任务模块 (scheduler.py)

- 每 6 小时自动爬取一次
- 支持手动触发爬取

### 4.4 前端展示 (dashboard/)

```
dashboard/
├── index.html       # 主页面
├── products.html   # 产品列表
├── price_history.html # 价格趋势
└── static/
    ├── style.css
    └── chart.js (CDN)
```

---

## 5. 品类与参数

### 5.1 扫地机器人

| 参数 | 说明 |
|------|------|
| 吸力 | Pa 或 AW |
| 续航 | 分钟 |
| 导航 | 激光/视觉/陀螺仪 |
| 避障 | 红外/AI/结构光 |
| 集尘盒容量 | mL |
| 水箱容量 | mL |
| 噪音 | dB |

### 5.2 智能门锁

| 参数 | 说明 |
|------|------|
| 开锁方式 | 指纹/密码/NFC/蓝牙/钥匙 |
| 锁芯等级 | C级/B级 |
| 供电 | 锂电池/干电池 |
| 特色 | 逗留抓拍/远程查看 |

### 5.3 智能音箱

| 参数 | 说明 |
|------|------|
| 麦克风数量 | 个 |
| 扬声器功率 | W |
| 屏幕 | 有/无/尺寸 |
| 生态 | 小爱/小度/天猫精灵 |

---

## 6. 页面设计

### 6.1 首页 (index.html)

- 概览统计卡片:
  - 总产品数
  - 今日更新数
  - 价格变动提醒
- 最近价格变动列表

### 6.2 产品列表 (products.html)

- 按品类筛选
- 按品牌筛选
- 搜索框
- 表格展示: 品牌 | 产品名 | 现价 | 历史最低 | 参数摘要

### 6.3 价格趋势 (price_history.html)

- Chart.js 折线图
- 选择产品查看历史价格
- 价格区间筛选

---

## 7. 目录结构

```
smart-home-price-tracker/
├── README.md
├── requirements.txt
├── config.yaml              # 配置文件
├── main.py                  # 入口文件
├── database.py              # 数据库操作
├── crawler.py               # 爬虫调度
├── models.py                # 数据模型
├── dashboard/
│   ├── index.html
│   ├── products.html
│   ├── price_history.html
│   └── static/
│       └── style.css
└── data/
    └── prices.db            # SQLite 数据库 (自动生成)
```

---

## 8. 使用方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行爬虫 (一次性)
python main.py crawl

# 3. 启动定时监控 (后台运行)
python main.py monitor

# 4. 打开 Dashboard
# 在浏览器中打开 dashboard/index.html
```

---

## 9. 合规声明

- 本工具仅用于学习和个人研究
- 爬取频率已限制，不会对目标网站造成压力
- 请勿用于商业盈利目的
- 数据版权归各电商平台和品牌方所有
