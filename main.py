"""
主程序入口
"""
import asyncio
from browser import BrowserManager
from data_handler import DataHandler
from qcc_scraper import QccScraper

async def main():
    print("============================================================")
    print("企查查社交媒体账号爬虫 - 启动中")
    print("============================================================")

    # 1. 读取名单
    companies = DataHandler.read_company_list()
    if not companies:
        print("❌ 没有找到有效的企业名单，请检查 Excel 文件。")
        return

    # 2. 启动浏览器并运行爬虫
    async with BrowserManager() as browser_manager:
        # 实例化爬虫逻辑类
        scraper = QccScraper(browser_manager)
        
        # 运行批量爬取
        await scraper.run(companies)

    print("\n============================================================")
    print("🎉 所有任务已结束！")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(main())