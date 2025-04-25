import json
import pandas as pd
import os

def load_job_details(folder_path):
    """加载指定文件夹中的职位详情"""
    json_path = os.path.join(folder_path, 'job_details.json')
    if not os.path.exists(json_path):
        return []
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_job_details(job_detai ls):
    """处理职位详情，提取所需信息"""
    processed_data = []
    for job in job_details:
        # 合并职位描述和要求为字符串
        desc_text = '\n'.join(job.get('职位描述', []))
        req_text = '\n'.join(job.get('职位要求', []))
        
        processed_data.append({
            '岗位名称': job.get('岗位名称', ''),
            '职位描述': desc_text,
            '职位要求': req_text,
            '大类': job.get('招聘大类', ''),
            '职位链接': job.get('url', '')
        })
    return processed_data

def main():
    # 定义文件夹路径
    folders = {
        '校招': '智元校招',
        '社招': '智元社招',
        '高招': '智元高招'
    }
    
    # 收集所有数据
    all_data = []
    for category, folder in folders.items():
        print(f"正在处理 {category} 数据...")
        job_details = load_job_details(folder)
        processed_data = process_job_details(job_details)
        all_data.extend(processed_data)
    
    # 创建DataFrame
    df = pd.DataFrame(all_data)
    
    # 保存为Excel
    output_file = '智元招聘汇总.xlsx'
    df.to_excel(output_file, index=False)
    print(f"\n数据已保存到 {output_file}")
    
    # 打印统计信息
    print(f"\n总共处理了 {len(all_data)} 条招聘信息")
    print("\n各类招聘数量统计：")
    print(df['大类'].value_counts())

if __name__ == "__main__":
    main()
