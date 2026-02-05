"""
企查查爬虫主逻辑模块
"""
import asyncio
import random
import re
from typing import Dict, List
from browser import BrowserManager
import config

class QccScraper:
    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self.page = browser_manager.page

    async def search_and_enter(self, company_name: str) -> tuple:
        """搜索并进入详情页，返回是否成功和实际点击的公司名称"""
        try:
            print(f"🔍 [1/3] 搜索: {company_name}")
            try:
                if "qcc.com" not in self.page.url or "search" in self.page.url:
                    await self.page.goto("https://www.qcc.com", timeout=30000)
                    await self.page.wait_for_load_state('domcontentloaded')
            except:
                await self.page.reload()

            search_input = await self.page.wait_for_selector(config.SELECTORS['search_input'], state='visible', timeout=10000)
            await search_input.fill("")
            await search_input.fill(company_name)
            await self.page.wait_for_timeout(500)
            await self.page.keyboard.press('Enter')

            await self.page.wait_for_load_state('domcontentloaded')

            target_link = self.page.locator(f"a:has-text('{company_name}')").first
            actual_click_name = company_name  # 默认为搜索名称

            try:
                await target_link.wait_for(state='visible', timeout=5000)
            except:
                print(f"   ⚠️ 未找到精确匹配，点击第一个结果...")
                target_link = self.page.locator("a.title").first
                # 获取实际点击的链接文本
                actual_click_name = await target_link.text_content()
                actual_click_name = actual_click_name.strip() if actual_click_name else company_name

            # 获取实际点击的链接文本
            if actual_click_name == company_name:
                actual_click_name = company_name
            else:
                actual_click_name = await target_link.text_content()
                actual_click_name = actual_click_name.strip() if actual_click_name else company_name

            async with self.page.context.expect_page() as new_page_info:
                await target_link.click()

            self.detail_page = await new_page_info.value
            await self.detail_page.wait_for_load_state('domcontentloaded')
            print(f"📄 [2/3] 进入详情页: {await self.detail_page.title()}")
            return True, actual_click_name
        except Exception as e:
            print(f"❌ 搜索进入失败: {e}")
            return False, company_name

    async def _auto_scroll(self):
        """【新增】自动滚屏，触发懒加载"""
        print("      -> 正在滚动页面加载数据...")
        try:
            # 滚到底部
            await self.detail_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.detail_page.wait_for_timeout(1000)
            # 滚回顶部
            await self.detail_page.evaluate("window.scrollTo(0, 0)")
            await self.detail_page.wait_for_timeout(500)
        except:
            pass

    async def _get_img_src(self, cell):
        """提取图片链接"""
        try:
            img = cell.locator('img').first
            if await img.count() > 0:
                src = await img.get_attribute('src')
                if src and "default" not in src:
                    return src
                return "有图片(默认图)"
            return ""
        except:
            return ""

    async def _resolve_real_url(self, link_element) -> str:
        """从中间过渡页提取目标链接（V3.0 源码扫描版）"""
        new_page = None
        try:
            # 1. 点击链接，捕获新页面
            async with self.page.context.expect_page() as new_page_info:
                await link_element.click()

            new_page = await new_page_info.value

            # === 阶段 1: 等待核心元素出现 (关键) ===
            # 不要只等 domcontentloaded，我们要等页面上真正出现 "weibo.com" 这几个字
            # 如果 3 秒内出现了，说明页面渲染好了
            try:
                await new_page.wait_for_selector("text=weibo.com", timeout=3000)
            except:
                pass # 超时也没关系，继续往下试

            # === 阶段 2: 检查是否已经跳转 ===
            if "weibo.com" in new_page.url and "qcc" not in new_page.url:
                final_url = new_page.url
                await new_page.close()
                return final_url

            # === 阶段 3: 上帝视角（扫描 HTML 源码） ===
            # 这是最稳的，不管它藏在 input 里还是 js 变量里，源码里一定有
            print("      -> 正在扫描页面源码...")
            html_content = await new_page.content() # 获取网页源代码

            # 正则匹配：匹配 weibo.com/后面跟数字或字母的格式
            # 这里的正则稍微放宽了一点，确保能匹配到
            match = re.search(r'(https?://(?:www\.)?weibo\.com/[A-Za-z0-9_]+)', html_content)

            if match:
                real_url = match.group(1)
                # 再次确认不是 www.weibo.com (主页)，而是带 ID 的
                if len(real_url) > 25:
                    print(f"      -> ⚡️ 源码提取成功: {real_url}")
                    await new_page.close()
                    return real_url

            # === 阶段 4: 点击按钮 (最后的加速手段) ===
            try:
                # 尝试点击页面上所有的 Button 类型的元素，只要包含“访问”或“前往”
                # 你的截图里按钮是蓝色的，通常有 btn 类
                btns = new_page.locator(".btn, button, a.btn").all()
                for btn in await btns:
                    txt = await btn.inner_text()
                    if "访问" in txt or "前往" in txt or "继续" in txt:
                        print(f"      -> 点击按钮: [{txt}]")
                        await btn.click()
                        await new_page.wait_for_url("**/weibo.com/**", timeout=4000)
                        if "weibo.com" in new_page.url:
                            final_url = new_page.url
                            print(f"      -> ⚡️ 按钮跳转成功: {final_url}")
                            await new_page.close()
                            return final_url
                        break
            except Exception as e:
                pass

            # === 阶段 5: 保底死等 ===
            print("      -> 只能死等自动跳转 (6秒)...")
            await new_page.wait_for_timeout(6000)

            if "weibo.com" in new_page.url:
                final_url = new_page.url
                print(f"      -> 保底跳转成功: {final_url}")
                await new_page.close()
                return final_url

            await new_page.close()
            return "解析失败(未跳转)"

        except Exception as e:
            print(f"   ⚠️ 链接解析出错: {e}")
            if new_page:
                try: await new_page.close()
                except: pass
            return ""

    async def extract_list_data(self, tab_name: str, col_map: dict) -> List[Dict]:
        """通用列表提取函数"""
        results = []
        try:
            # 1. 【暴力查找 Tab】尝试多种选择器
            # 企查查的 Tab 可能是 <a> 也可能是 <li> 或者是 <span>
            possible_selectors = [
                f"a:has-text('{tab_name}')",
                f"li:has-text('{tab_name}')",
                f"span:has-text('{tab_name}')"
            ]

            target_tab = None
            for sel in possible_selectors:
                elements = await self.detail_page.locator(sel).all()
                for el in elements:
                    if await el.is_visible():
                        text = await el.inner_text()
                        # 确保不是别的无关链接，比如底部导航
                        if tab_name in text and len(text) < 15:
                            target_tab = el
                            break
                if target_tab: break

            if target_tab:
                text = await target_tab.inner_text()
                # 检查 (0)
                if "(0)" in text or text.strip().endswith(" 0") or text.strip() == tab_name + "0":
                    return []

                # 点击并等待
                await target_tab.click()
                await self.detail_page.wait_for_timeout(1000)
            else:
                # 找不到Tab，可能已经在当前页面显示了，或者真没有
                pass

            # 2. 【暴力查找表格】
            # 获取所有表格，逐个检查内容
            tables = await self.detail_page.locator('table').all()
            target_table = None

            check_text = "微信号" if tab_name == "微信公众号" else "微博昵称"

            for t in tables:
                table_text = await t.inner_text()
                if check_text in table_text:
                    target_table = t
                    break

            if not target_table:
                return []

            # 3. 解析表格
            rows = await target_table.locator('tr').all()

            for row in rows:
                cols = await row.locator('td').all()
                if not cols or len(cols) < 3: continue

                item = {}

                # 序号
                if 'seq' in col_map and len(cols) > col_map['seq']:
                    item['seq'] = await cols[col_map['seq']].inner_text()

                # 头像
                if 'avatar' in col_map and len(cols) > col_map['avatar']:
                    item['avatar'] = await self._get_img_src(cols[col_map['avatar']])

                # 名称 & 链接
                if 'name' in col_map and len(cols) > col_map['name']:
                    cell = cols[col_map['name']]
                    item['name'] = (await cell.inner_text()).strip()

                    link_elem = cell.locator('a').first
                    if await link_elem.count() > 0:
                        if tab_name == "微博":
                            item['link'] = await self._resolve_real_url(link_elem)
                        else:
                            item['link'] = await link_elem.get_attribute('href')
                    else:
                        item['link'] = ""

                # 微信号
                if 'wechat_id' in col_map and len(cols) > col_map['wechat_id']:
                    item['wechat_id'] = (await cols[col_map['wechat_id']].inner_text()).strip()

                # 二维码
                if 'qr' in col_map and len(cols) > col_map['qr']:
                    item['qr'] = await self._get_img_src(cols[col_map['qr']])

                if item:
                    results.append(item)

            return results

        except Exception as e:
            # print(f"   ⚠️ 提取 {tab_name} 列表出错: {e}") # 调试时可打开
            return []

    async def scrape_details(self, company_name: str, actual_click_name: str = None) -> Dict:
        """[3/3] 提取详细信息"""
        data = {
            'company_name': company_name,
            'actual_click_name': actual_click_name or company_name,
            'wechat_list': [],
            'weibo_list': [],
            'status': 'success',
            'error': ''
        }

        try:
            # 1. 【关键】先滚屏，加载数据
            await self._auto_scroll()

            # 2. 尝试点击知识产权导航
            # 尝试多种定位器，直到点中为止
            nav_clicked = False
            ip_selectors = [
                config.SELECTORS['nav_ip'],
                "a:has-text('知识产权')",
                "h2:has-text('知识产权')", # 这里的点击可能是为了滚动的锚点
                ".nav-item:has-text('知识产权')"
            ]

            for sel in ip_selectors:
                try:
                    el = self.detail_page.locator(sel).first
                    if await el.is_visible():
                        print("   └── 点击【知识产权】...")
                        await el.click()
                        await self.detail_page.wait_for_timeout(1000)
                        nav_clicked = True
                        break
                except:
                    continue

            if not nav_clicked:
                print("   ⚠️ 未找到顶部导航，尝试直接搜索页面表格...")

            # 3. 抓取数据
            print("   └── 抓取微信公众号列表...")
            data['wechat_list'] = await self.extract_list_data("微信公众号", config.WECHAT_COL_INDEX)

            print("   └── 抓取微博列表...")
            data['weibo_list'] = await self.extract_list_data("微博", config.WEIBO_COL_INDEX)

        except Exception as e:
            print(f"   ❌ 提取详情出错: {e}")
            data['error'] = str(e)
            data['status'] = 'failed'

        finally:
            if hasattr(self, 'detail_page'):
                await self.detail_page.close()

        return data

    async def run(self, company_list: List[str]):
        """运行入口"""
        all_raw_data = []

        for i, company in enumerate(company_list):
            print(f"\n[{i+1}/{len(company_list)}] 处理: {company}")

            success, actual_click_name = await self.search_and_enter(company)
            if success:
                raw_data = await self.scrape_details(company, actual_click_name)
                # 添加匹配状态到数据中
                raw_data['match_status'] = '匹配' if company == actual_click_name else '不匹配'
                all_raw_data.append(raw_data)

                wait = random.uniform(2, 4)
                print(f"   💤 等待 {wait:.1f} 秒...")
                await self.page.wait_for_timeout(wait * 1000)
            else:
                all_raw_data.append({
                    'company_name': company,
                    'actual_click_name': company,
                    'match_status': 'search_failed',
                    'status': 'failed',
                    'error': '搜索失败'
                })

            if (i + 1) % 2 == 0:
                from data_handler import DataHandler
                DataHandler.save_formatted_results(all_raw_data)

        from data_handler import DataHandler
        DataHandler.save_formatted_results(all_raw_data)