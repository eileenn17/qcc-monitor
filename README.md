# 企查查社交媒体账号爬虫项目

通过 Playwright 模拟浏览器自动化爬取企查查上的企业社交媒体账号信息，包括微博、微信公众号等。

## 项目特点

- ✅ 自动读取 Excel 企业名单
- ✅ 自动化搜索 → 点击详情 → 抓取社交媒体数据
- ✅ 支持错误重试和异常处理
- ✅ 数据自动保存为 Excel
- ✅ 新增曾用名字段，支持显示企业曾用名
- ✅ 自动规范化中英文括号，避免匹配错误
- ✅ 输入文件独立管理，安全隔离

## 项目结构

```
qcc_monitor/
├── config.py              # 配置文件管理
├── browser.py             # 浏览器初始化和管理
├── qcc_scraper.py         # 企查查爬虫主逻辑
├── data_handler.py        # 数据读写处理
├── main.py                # 主程序入口
├── login_tool.py          # 手动登录辅助工具
├── requirements.txt       # 依赖包列表
├── .env.example           # 环境变量示例
├── README.md              # 项目文档
├── input/                 # 输入数据目录
└── output/                # 输出数据目录
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd qcc_monitor

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

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

在 `input/` 目录下放置 Excel 文件（默认名为 `企业名单（爬虫测试版）.xlsx`），格式为：

| 企业名称 | 其他字段... |
|----------|-------------|
| 企业A    | ...         |
| 企业B    | ...         |

### 4. 手动登录企查查

首次使用前，需要手动登录企查查以复用登录状态：

```bash
python login_tool.py
```

在打开的浏览器中登录企查查账号，登录成功后按回车键退出。

### 5. 运行爬虫

```bash
python main.py
```

## 输出数据字段

爬虫完成后，将在 `output/` 目录生成 Excel 文件，包含以下字段：

- 公司名称
- 实际点击公司名
- 搜索匹配状态
- 曾用名
- 微信公众号总个数
- 序号(微信)
- 头像(微信)
- 微信公众号名称
- 微信号
- 二维码
- 微博账号总个数
- 序号(微博)
- 头像(微博)
- 微博昵称
- 微博链接
- status

## 功能特性

### 曾用名提取
- 自动从企查查搜索结果中提取企业曾用名
- 在输出中新增"曾用名"列，显示曾用名或"无"

### 括号规范化
- 自动将英文括号转换为中文括号
- 避免因中英文括号差异导致的匹配错误

### 智能匹配
- 支持精确匹配、曾用名匹配和不匹配三种状态
- 提供详细的匹配状态信息

### 数据安全
- 输入文件独立存放在 `input/` 目录
- `input/` 目录已加入 `.gitignore`，防止敏感数据泄露

## 常见问题

### Q: 登录状态失效怎么办？

A: 重新运行 `login_tool.py` 手动登录，或在本地 Chrome 中登录企查查，爬虫会自动读取最新的登录状态。

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
- ⚠️ 请勿将包含敏感信息的文件提交到版本控制系统

## 后续扩展

- [ ] 添加数据库存储
- [ ] 集成定时任务（定期监测更新）
- [ ] IP代理池支持

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。