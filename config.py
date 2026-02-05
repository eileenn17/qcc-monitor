"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 路径配置
CHROME_USER_DATA_DIR = os.getenv(
    'CHROME_USER_DATA_DIR',
    os.path.expanduser('~/Library/Application Support/Google/Chrome')
)
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
INPUT_FILE = str(BASE_DIR / 'input' / '企业名单（爬虫测试版）.xlsx')
OUTPUT_FILE = str(BASE_DIR / 'output' / '企业社交媒体账号库.xlsx')

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_DIR = BASE_DIR / 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

# 基础配置
QCC_SEARCH_URL = "https://www.qcc.com"
TIMEOUT = 30000
WAIT_TIME = 1500
HEADLESS = False 
RETRY_TIMES = 3

# 【关键修复】补回 PROXY 配置，防止 browser.py 报错
PROXY = os.getenv('PROXY', None)

# === 选择器配置 ===
SELECTORS = {
    'search_input': '#searchKey',
    'nav_ip': 'a:has-text("知识产权")', # 知识产权导航
}

# === 表格列索引配置 ===
# 注意：Playwright 的 nth(index) 是从 0 开始的

# 微信表格结构：序号(0), 头像(1), 微信公众号(2), 微信号(3), 二维码(4), 简介(5)
WECHAT_COL_INDEX = {
    'seq': 0,      # 序号
    'avatar': 1,   # 头像 (img)
    'name': 2,     # 微信公众号名称
    'wechat_id': 3,# 微信号
    'qr': 4,       # 二维码 (img)
}

# 微博表格结构：序号(0), 头像(1), 微博昵称(2), 简介(3)
WEIBO_COL_INDEX = {
    'seq': 0,      # 序号
    'avatar': 1,   # 头像
    'name': 2,     # 微博昵称
}