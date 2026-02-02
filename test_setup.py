"""
测试脚本 - 验证爬虫是否工作正常
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from browser import BrowserManager
import config


async def test_browser_init():
    """测试浏览器初始化"""
    print("=" * 60)
    print("测试 1: 浏览器初始化")
    print("=" * 60)
    
    try:
        browser_manager = BrowserManager()
        await browser_manager.init_browser()
        print("✅ 浏览器初始化成功")
        
        # 测试导航
        print("\n测试导航到企查查...")
        await browser_manager.navigate(config.QCC_SEARCH_URL)
        print("✅ 导航成功")
        
        # 等待用户观察
        print("\n浏览器已打开，请检查是否成功加载企查查页面")
        print("5 秒后自动关闭浏览器...")
        await browser_manager.page.wait_for_timeout(5000)
        
        await browser_manager.close()
        print("\n✅ 浏览器关闭成功")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_config():
    """测试配置"""
    print("\n" + "=" * 60)
    print("测试 2: 配置检查")
    print("=" * 60)
    
    checks = {
        "Chrome 用户数据目录": Path(config.CHROME_USER_DATA_DIR).exists(),
        "输出目录": Path(config.OUTPUT_DIR).exists(),
        "Timeout 设置": config.TIMEOUT > 0,
        "重试次数": config.RETRY_TIMES > 0,
    }
    
    all_passed = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}: {result}")
        if not result:
            all_passed = False
    
    # 详细输出关键配置
    print("\n配置详情:")
    print(f"  Chrome 数据目录: {config.CHROME_USER_DATA_DIR}")
    print(f"  输出目录: {config.OUTPUT_DIR}")
    print(f"  超时时间: {config.TIMEOUT}ms")
    print(f"  等待时间: {config.WAIT_TIME}ms")
    print(f"  重试次数: {config.RETRY_TIMES}")
    
    return all_passed


async def test_data_handler():
    """测试数据处理"""
    print("\n" + "=" * 60)
    print("测试 3: 数据处理")
    print("=" * 60)
    
    try:
        from data_handler import DataHandler
        
        # 测试读取（如果文件存在）
        input_file = Path(config.INPUT_FILE)
        if input_file.exists():
            companies = DataHandler.read_company_list()
            print(f"✅ 成功读取 {len(companies)} 家企业")
        else:
            print(f"⚠️  企业名单文件不存在: {config.INPUT_FILE}")
            print("   请先创建 Excel 文件并放在项目目录")
        
        # 测试数据保存（模拟）
        test_data = [
            {
                'company_name': '测试企业',
                'status': 'success',
                'website': 'https://example.com',
                'weibo_account': '@test',
                'weibo_url': 'https://weibo.com/test',
                'error': None,
            }
        ]
        
        output_file = config.OUTPUT_DIR / 'test_output.xlsx'
        DataHandler.save_results(test_data, str(output_file))
        
        if output_file.exists():
            print(f"✅ 数据保存成功: {output_file}")
            output_file.unlink()  # 删除测试文件
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def main():
    """运行所有测试"""
    print("\n" + "🧪 企查查爬虫项目 - 自诊断测试 🧪".center(60))
    print("\n")
    
    results = {}
    
    # 配置测试
    results['配置检查'] = await test_config()
    
    # 数据处理测试
    results['数据处理'] = await test_data_handler()
    
    # 浏览器测试（可选，需要手动确认）
    print("\n" + "=" * 60)
    response = input("是否进行浏览器初始化测试？(y/n) [n]: ").strip().lower()
    if response == 'y':
        results['浏览器初始化'] = await test_browser_init()
    
    # 测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！可以开始爬虫任务")
    else:
        print("❌ 部分测试失败，请查看上面的错误信息并修复")
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    if sys.platform == 'darwin':
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被中断")
        sys.exit(1)
