"""
浏览器初始化和管理模块
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import config


class BrowserManager:
    """浏览器管理类"""
    
    def __init__(self):
        self.context = None
        self.page = None
        self.playwright = None
    
    async def init_browser(self):
        """
        初始化浏览器，使用持久化上下文（携带用户数据）
        """
        try:
            self.playwright = await async_playwright().start()
            
            # 1. 准备用户数据目录
            user_data_dir = Path(config.CHROME_USER_DATA_DIR).expanduser()
            if not user_data_dir.exists():
                user_data_dir.mkdir(parents=True, exist_ok=True)
                print(f"📁 已创建新的用户数据目录: {user_data_dir}")
            
            # 2. 准备启动参数
            launch_args = {
                'headless': config.HEADLESS,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ],
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # 如果有代理，添加代理配置
            if config.PROXY:
                launch_args['proxy'] = {'server': config.PROXY}
            
            print(f"🚀 正在启动浏览器 (使用数据目录: {user_data_dir})...")
            
            # 3. 核心：使用 launch_persistent_context
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                **launch_args
            )
            
            # 4. 获取页面
            if len(self.context.pages) > 0:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()
            
            print("✅ 浏览器初始化成功")
            
            # 【关键修复】这里必须返回 self，否则 main.py 接收到的是 None
            return self
            
        except Exception as e:
            print(f"❌ 浏览器初始化失败: {e}")
            raise
    
    async def close(self):
        """关闭浏览器"""
        try:
            # 检查对象是否存在再关闭，防止报错
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
            print("✅ 浏览器已关闭")
        except Exception as e:
            # 忽略关闭时的错误，避免掩盖主逻辑的报错
            print(f"⚠️ 关闭浏览器时发生轻微错误: {e}")
    
    async def __aenter__(self):
        # 1. 初始化浏览器
        await self.init_browser()
        # 2. 返回 self (BrowserManager实例)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()