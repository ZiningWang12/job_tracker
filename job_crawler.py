import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import os

def get_job_links(url):
    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # 初始化浏览器
    driver = webdriver.Chrome(options=options)
    job_links = []
    
    try:
        # 访问页面
        driver.get(url)
        
        # 等待页面加载
        time.sleep(5)  # 给页面足够的时间加载
        
        # 等待职位列表加载
        wait = WebDriverWait(driver, 10)
        job_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/position/"]')))
        
        # 获取所有职位链接
        for job in job_elements:
            href = job.get_attribute('href')
            if href and href not in job_links:
                job_links.append(href)
                print(f"找到职位链接: {href}")
        
        print(f"\n总共找到 {len(job_links)} 个职位链接")
        
    except Exception as e:
        print(f"获取链接时出错: {str(e)}")
    
    finally:
        # 关闭浏览器
        driver.quit()
    
    return job_links

def save_job_links(job_links):
    # 保存链接到文件
    with open('job_links.txt', 'w', encoding='utf-8') as f:
        for link in job_links:
            f.write(link + '\n')

def get_job_details(job_url,recruit_category='未知'):
    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        # 初始化浏览器
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 访问页面
        driver.get(job_url)
        time.sleep(3)  # 等待页面加载
        
        # 获取页面文本
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        
        # 使用正则表达式提取信息
        job_info = {
            '招聘大类': recruit_category,
            '岗位名称': '',
            '工作地点': '',
            '职位描述': [],
            '职位要求': [],
            'url': job_url,
            'raw_text': page_text
        }
        
        # 提取岗位名称和工作地点
        lines = page_text.split('\n')
        for i, line in enumerate(lines):
            if line.strip() and not any(keyword in line for keyword in ['登录', '职位描述', '职位要求', '投递']):
                if not job_info['岗位名称']:
                    job_info['岗位名称'] = line.strip()
                elif not job_info['工作地点']:
                    job_info['工作地点'] = line.strip()
                else:
                    break
        
        # 提取职位描述
        desc_start = page_text.find('职位描述')
        req_start = page_text.find('职位要求')
        if desc_start != -1 and req_start != -1:
            desc_text = page_text[desc_start + 4:req_start].strip()
            # 分割成列表项
            desc_items = []
            current_item = ''
            for line in desc_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                if re.match(r'^\d+[、.]', line):
                    if current_item:
                        desc_items.append(current_item.strip())
                    current_item = line
                else:
                    current_item += ' ' + line
            if current_item:
                desc_items.append(current_item.strip())
            job_info['职位描述'] = desc_items
        
        # 提取职位要求
        if req_start != -1:
            req_text = page_text[req_start + 4:].strip()
            # 分割成列表项
            req_items = []
            current_item = ''
            for line in req_text.split('\n'):
                line = line.strip()
                if not line or '投递' in line:
                    continue
                if re.match(r'^\d+[、.]', line):
                    if current_item:
                        req_items.append(current_item.strip())
                    current_item = line
                else:
                    current_item += ' ' + line
            if current_item:
                req_items.append(current_item.strip())
            job_info['职位要求'] = req_items
        
        print(f"已获取职位信息: {job_info['岗位名称']}")
        return job_info
        
    except Exception as e:
        print(f"获取职位详情出错: {str(e)}")
        return None
        
    finally:
        try:
            driver.quit()
        except:
            pass


def get_zhiyuan_jobs():
    #社招
    url1 = "https://agirobot.jobs.feishu.cn/socialrecruitment/?keywords=&category=6937213309162752293%2C6791702736615426317%2C6791702736615409933&location=&project=&type=&job_hot_flag=&current=1&limit=100&functionCategory=&tag="
    #高级
    url2 = "https://agirobot.jobs.feishu.cn/index/?keywords=&category=&location=&project=&type=&job_hot_flag=&current=1&limit=20&functionCategory=&tag="
    #校招
    url3 = "https://agirobot.jobs.feishu.cn/campusrecruitment/?keywords=&category=&location=&project=&type=&job_hot_flag=&current=1&limit=30&functionCategory=&tag="
    #实习
    url4 = "https://agirobot.jobs.feishu.cn/internrecruitment/?keywords=&category=6937213309162752293%2C6791702736615426317&location=&project=&type=&job_hot_flag=&current=1&limit=10&functionCategory=&tag="
    url_dict = {
        "校招": url3,
        "实习": url4,
        "高级": url2,
        "社招": url1
    }
    
    # 爬取智元招聘
    job_links = {}
    for category, url in url_dict.items():
        job_links[category] = get_job_links(url)
        save_job_links(job_links[category])

    # 保存智元招聘链接至json
    with open('job_links.json', 'w', encoding='utf-8') as f:
        json.dump(job_links, f, ensure_ascii=False, indent=2)

    # 读取智元招聘职位链接
    with open('job_links.json', 'r', encoding='utf-8') as f:
        job_links = json.load(f)
    
    # 获取所有智元招聘职位详情
    all_jobs = []
    for category, links in job_links.items():
        for i, link in enumerate(links, 1):
            print(f"\n正在处理第 {i}/{len(links)} 个智元招聘职位...")
            job_info = get_job_details(link, recruit_category=category)
            if job_info:
                all_jobs.append(job_info)
            time.sleep(2)
    return all_jobs

def get_figure_jobs():
    """爬取 Figure AI 的招聘信息"""
    url = "https://www.figure.ai/careers#careers-listing"
    
    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        # 初始化浏览器
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 访问页面
        driver.get(url)
        print("等待页面加载...")
        time.sleep(5)  # 等待页面加载
        
        # 获取页面内容
        page_source = driver.page_source
        
        # 解析HTML
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 获取所有职位链接
        job_links = []
        for a in soup.find_all('a'):
            href = a.get('href')
            if href and 'greenhouse.io/figureai/jobs/' in href:
                job_links.append(href)
                print(f"找到职位链接: {href}")
        
        print(f"\n总共找到 {len(job_links)} 个职位链接")
        
        # 获取每个职位的详细信息
        job_details = []
        for i, job_url in enumerate(job_links, 1):
            print(f"\n正在处理第 {i}/{len(job_links)} 个职位...")
            try:
                # 访问职位页面
                driver.get(job_url)
                time.sleep(3)  # 等待页面加载
                
                # 获取职位页面内容
                job_soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # 提取职位信息
                title = job_soup.find('h1', class_='app-title').text.strip() if job_soup.find('h1', class_='app-title') else '未知'
                location = job_soup.find('div', class_='location').text.strip() if job_soup.find('div', class_='location') else '未知'
                
                # 提取职位描述和要求
                description = []
                requirements = []
                
                # 查找所有段落
                for p in job_soup.find_all('p'):
                    text = p.text.strip()
                    if text:
                        if 'responsibilities' in text.lower() or 'description' in text.lower():
                            description.append(text)
                        elif 'requirements' in text.lower() or 'qualifications' in text.lower():
                            requirements.append(text)
                
                # 如果没有找到明确的描述和要求，则获取所有文本
                if not description and not requirements:
                    content = job_soup.find('div', class_='opening')
                    if content:
                        all_text = content.text.strip()
                        description = [all_text]
                
                job_info = {
                    '招聘大类': 'Figure AI',
                    '岗位名称': title,
                    '工作地点': location,
                    '职位描述': description,
                    '职位要求': requirements,
                    'url': job_url
                }
                
                job_details.append(job_info)
                print(f"已获取职位信息: {title}")
                
                # 保存到文件
                with open('figure_jobs.json', 'w', encoding='utf-8') as f:
                    json.dump(job_details, f, ensure_ascii=False, indent=2)
                
            except Exception as e:
                print(f"处理职位 {job_url} 时出错: {str(e)}")
                continue
        
        return job_details
        
    except Exception as e:
        print(f"获取 Figure AI 职位信息出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
        
    finally:
        try:
            driver.quit()
        except:
            pass

def main():
    all_jobs = []
    '''
    # 原有的智元招聘爬取
    zhiyuan_jobs = get_zhiyuan_jobs()
    all_jobs.extend(zhiyuan_jobs)
    '''
    
    # 爬取 Figure AI 职位
    print("\n开始爬取 Figure AI 职位...")
    figure_jobs = get_figure_jobs()
    all_jobs.extend(figure_jobs)
    
    # 保存所有职位信息到JSON文件
    with open('job_details.json', 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)
    
    print(f"\n总共获取到 {len(all_jobs)} 个职位信息")
    print("所有职位信息已保存到 job_details.json")

if __name__ == "__main__":
    main()