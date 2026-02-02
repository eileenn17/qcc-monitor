# 企查查社交媒体账号爬虫项目

通过 Playwright 模拟浏览器自动化爬取企查查上的企业社交媒体账号信息。

## 项目特点

- ✅ 复用本地 Chrome 登录状态，无需重复登录
- ✅ 自动读取 Excel 企业名单
- ✅ 自动化搜索 → 点击详情 → 抓取社交媒体数据
- ✅ 支持错误重试和异常处理
- ✅ 数据自动保存为 Excel

## 项目结构

```
qcc_monitor/
├── config.py              # 配置文件管理
├── browser.py             # 浏览器初始化和管理
├── qcc_scraper.py         # 企查查爬虫主逻辑
├── data_handler.py        # 数据读写处理
├── main.py                # 主程序入口
├── requirements.txt       # 依赖包列表
├── .env.example           # 环境变量示例
├── .env                   # 环境变量（本地）
├── README.md              # 项目文档
└── output/                # 输出数据目录
    └── 企业社交媒体账号库.xlsx
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 配置本地 Chrome 用户数据

复制 `.env.example` 为 `.env` 并修改：

```bash
cp .env.example .env
```

编辑 `.env`，找到你的 Chrome 用户数据目录：

**macOS:**
```
/Users/your_username/Library/Application Support/Google/Chrome
```

**Windows:**
```
C:\Users\your_username\AppData\Local\Google\Chrome\User Data
```

**Linux:**
```
/home/your_username/.config/google-chrome
```

### 3. 准备企业名单

在项目根目录放置 `企业名单.xlsx` 文件，格式为：

| 企业名称 | 其他字段... |
|--------|-----------|
| 企业A   | ...       |
| 企业B   | ...       |

### 4. 运行爬虫

```bash
python main.py
```

## 工作流程

1. **初始化浏览器**：使用本地 Chrome 用户数据启动浏览器
2. **读取名单**：从 Excel 读取企业名称
3. **循环处理**：
   - 搜索企业
   - 进入企业详情页
   - 提取社交媒体账号信息
   - 保存数据
4. **数据导出**：保存为 Excel 文件

## 爬取的数据字段

- 企业名称
- 官网链接
- 微博账号
- 微博粉丝数
- 微博链接
- 抖音账号
- 抖音粉丝数
- 抖音链接
- 小红书账号
- 小红书粉丝数
- 小红书链接
- 微信公众号
- 微信公众号链接
- 其他社交媒体

## 常见问题

### Q: 登录状态失效怎么办？

A: 重新在本地 Chrome 中登录企查查，爬虫会自动读取最新的登录状态。

### Q: 爬虫被检测了怎么办？

A: 
1. 添加随机延迟
2. 使用代理 IP
3. 调整请求头信息
4. 联系企查查申请爬虫权限

### Q: 如何处理网页加载不完全？

A: 调整 `qcc_scraper.py` 中的等待时间和选择器。

## 注意事项

- ⚠️ 请遵守网站的爬虫协议和法律规定
- ⚠️ 建议添加适当延迟，避免对服务器造成压力
- ⚠️ 定期检查登录状态是否有效
- ⚠️ 爬虫被检测时请停止运行

## 后续扩展

- [ ] 添加数据库存储
- [ ] 集成定时任务（定期监测更新）
- [ ] 添加日志记录
- [ ] 集成 AI 内容分析
- [ ] Web 仪表板展示
