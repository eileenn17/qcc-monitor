"""
数据读写处理模块 (适配复杂 Excel 表头 + 微博链接 + 无数据标记)
"""
from pathlib import Path
from typing import List, Dict
import pandas as pd
import config

class DataHandler:
    
    @staticmethod
    def read_company_list(file_path: str = None) -> List[str]:
        """读取企业名单"""
        if file_path is None: file_path = config.INPUT_FILE
        
        try:
            file_path = Path(file_path)
            print(f"📁 正在读取 Excel: {file_path.name}")
            
            df = pd.read_excel(file_path, header=None)
            
            target_col_index = -1
            start_row_index = -1
            found = False
            
            # 智能扫描表头
            for r in range(min(5, len(df))):
                for c in range(len(df.columns)):
                    cell_value = str(df.iloc[r, c]).strip()
                    if "企业名称" in cell_value:
                        target_col_index = c
                        start_row_index = r + 1
                        print(f"✅ 定位成功：在第 {r+1} 行，第 {c+1} 列找到表头")
                        found = True
                        break
                if found: break
            
            if found:
                raw_names = df.iloc[start_row_index:, target_col_index].dropna().astype(str).tolist()
            else:
                print("⚠️ 没找到‘企业名称’表头，尝试默认读取第2列...")
                if len(df.columns) > 1:
                    raw_names = df.iloc[2:, 1].dropna().astype(str).tolist()
                else:
                    return []

            clean_names = []
            for name in raw_names:
                name = name.strip()
                if len(name) > 1 and not name.isdigit() and "企业名称" not in name:
                    clean_names.append(name)
            
            print(f"✅ 成功提取 {len(clean_names)} 家有效企业")
            return clean_names

        except Exception as e:
            print(f"❌ 读取失败: {e}")
            return []

    @staticmethod
    def save_formatted_results(raw_data_list: List[Dict], output_file: str = None):
        """核心保存函数"""
        if output_file is None: output_file = config.OUTPUT_FILE
        
        excel_rows = []

        for data in raw_data_list:
            company_name = data.get('company_name', '')
            wechat_list = data.get('wechat_list', [])
            weibo_list = data.get('weibo_list', [])
            status = data.get('status', '')

            max_rows = max(len(wechat_list), len(weibo_list), 1)

            for i in range(max_rows):
                row = {}
                
                # === 第一部分：公司基本信息 ===
                if i == 0:
                    row['公司名称'] = company_name
                    row['微信公众号总个数'] = len(wechat_list)
                else:
                    row['公司名称'] = ''
                    row['微信公众号总个数'] = ''

                # === 第二部分：微信详情 ===
                if i < len(wechat_list):
                    # 有数据的情况
                    wc = wechat_list[i]
                    row['序号(微信)'] = wc.get('seq', '')
                    row['头像(微信)'] = wc.get('avatar', '')
                    row['微信公众号名称'] = wc.get('name', '')
                    row['微信号'] = wc.get('wechat_id', '')
                    row['二维码'] = wc.get('qr', '')
                else:
                    # 没有数据，或者行数超出的情况
                    if i == 0 and len(wechat_list) == 0:
                        # 【修改点】如果是第一行且列表为空，标记无数据
                        row['序号(微信)'] = '-'
                        row['头像(微信)'] = '-'
                        row['微信公众号名称'] = '无数据'
                        row['微信号'] = '无数据'
                        row['二维码'] = '-'
                    else:
                        # 只是用来占位的空行
                        row['序号(微信)'] = ''
                        row['头像(微信)'] = ''
                        row['微信公众号名称'] = ''
                        row['微信号'] = ''
                        row['二维码'] = ''

                # === 第三部分：微博总数 ===
                if i == 0:
                    row['微博账号总个数'] = len(weibo_list)
                else:
                    row['微博账号总个数'] = ''

                # === 第四部分：微博详情 ===
                if i < len(weibo_list):
                    # 有数据的情况
                    wb = weibo_list[i]
                    row['序号(微博)'] = wb.get('seq', '')
                    row['头像(微博)'] = wb.get('avatar', '')
                    row['微博昵称'] = wb.get('name', '')
                    row['微博链接'] = wb.get('link', '') 
                else:
                    # 没有数据，或者行数超出的情况
                    if i == 0 and len(weibo_list) == 0:
                        # 【修改点】如果是第一行且列表为空，标记无数据
                        row['序号(微博)'] = '-'
                        row['头像(微博)'] = '-'
                        row['微博昵称'] = '无数据'
                        row['微博链接'] = '无数据'
                    else:
                        # 只是用来占位的空行
                        row['序号(微博)'] = ''
                        row['头像(微博)'] = ''
                        row['微博昵称'] = ''
                        row['微博链接'] = ''

                # === 第五部分：状态 ===
                if i == 0:
                    row['status'] = status
                
                excel_rows.append(row)

        try:
            columns = [
                '公司名称', 
                '微信公众号总个数', '序号(微信)', '头像(微信)', '微信公众号名称', '微信号', '二维码',
                '微博账号总个数', '序号(微博)', '头像(微博)', '微博昵称', '微博链接',
                'status' 
            ]
            
            df = pd.DataFrame(excel_rows)
            for col in columns:
                if col not in df.columns:
                    df[col] = ''
            
            df = df[columns]

            path = Path(output_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(path, index=False)
            print(f"✅ Excel 已更新: {output_file}")
            
        except Exception as e:
            print(f"❌ 保存 Excel 失败: {e}")