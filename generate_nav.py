# generate_nav.py
import os
import glob
from bs4 import BeautifulSoup # 需要安装: pip install beautifulsoup4

# HTML 卡片模板
# 注意：这里的 class 名称需要和 index.html 中的 CSS 定义一致
CARD_TEMPLATE = """
<a href="{link_path}" class="card">
    <h2 class="card-title">{title}</h2>
    <p class="card-description">{description}</p>
</a>
"""

# 导航内容的占位符，必须与 index.html 中的占位符完全一致
NAV_PLACEHOLDER = """<!-- 示例卡片结构 (将被脚本替换):
<a href="path/to/your_file.html" class="card">
    <h2 class="card-title">示例文件名</h2>
    <p class="card-description">这是从 meta 标签或 title 标签提取的描述信息。</p>
</a>
-->"""

def extract_details(html_filepath):
    """
    从指定的 HTML 文件中提取标题和描述。
    """
    page_title = os.path.splitext(os.path.basename(html_filepath))[0].replace('_', ' ').replace('-', ' ').title() # 默认标题为文件名
    description = "暂无描述。" # 默认描述

    try:
        with open(html_filepath, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

            # 1. 尝试获取 <title> 标签内容
            title_tag = soup.title
            if title_tag and title_tag.string:
                page_title = title_tag.string.strip()

            # 2. 尝试获取 <meta name="description"> 的内容
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_desc_tag and meta_desc_tag.get('content'):
                description = meta_desc_tag.get('content').strip()
            elif page_title != os.path.splitext(os.path.basename(html_filepath))[0].replace('_', ' ').replace('-', ' ').title():
                # 如果没有 meta description，但成功获取了 <title>，则用 title 作为描述
                description = page_title
                
    except Exception as e:
        print(f"处理文件 '{html_filepath}' 时发生错误: {e}")
        # 保留默认值
    
    return page_title, description

def main():
    """
    主函数，扫描HTML文件，生成导航链接，并更新 index.html。
    """
    print("开始生成导航链接...")
    base_dir = os.getcwd() # 获取当前工作目录，即仓库根目录
    all_cards_html = []

    # 扫描仓库中所有的 HTML 文件，排除 index.html 和特定目录
    # 使用 recursive=True 来扫描子目录
    # 使用 os.path.join 来构建路径，确保跨平台兼容性
    excluded_dirs = {'.git', '.github', 'venv', 'node_modules'} # 集合用于快速查找

    for filepath_absolute in glob.glob(os.path.join(base_dir, '**', '*.html'), recursive=True):
        # 转换为相对于仓库根目录的路径
        relative_filepath = os.path.relpath(filepath_absolute, base_dir)

        # 检查是否在排除目录中
        path_parts = relative_filepath.split(os.sep)
        if any(part in excluded_dirs for part in path_parts):
            # print(f"跳过排除目录中的文件: {relative_filepath}")
            continue
            
        # 排除 index.html 文件本身
        if os.path.basename(relative_filepath).lower() == 'index.html':
            # print(f"跳过导航文件自身: {relative_filepath}")
            continue

        print(f"找到文件: {relative_filepath}")
        title, desc = extract_details(filepath_absolute)
        
        # 将文件路径转换为URL友好的相对路径 (使用 /)
        link_path = relative_filepath.replace(os.sep, '/')
        
        card_html = CARD_TEMPLATE.format(link_path=link_path, title=title, description=desc)
        all_cards_html.append(card_html)

    if not all_cards_html:
        print("未找到任何可供导航的 HTML 文件。")
        # 如果没有卡片，nav_content 将是空字符串，会清空占位符区域
        nav_content = ""
    else:
        print(f"共生成 {len(all_cards_html)} 个导航卡片。")
        nav_content = "\n".join(all_cards_html)

    # 读取 index.html 的内容
    index_html_path = os.path.join(base_dir, 'index.html')
    try:
        with open(index_html_path, 'r', encoding='utf-8') as file:
            index_content_original = file.read()
    except FileNotFoundError:
        print(f"错误: 导航文件 '{index_html_path}' 未找到。请确保它存在于仓库根目录。")
        return

    # 检查 NAV_PLACEHOLDER 是否为空 (理论上不应该，因为它是硬编码的)
    if not NAV_PLACEHOLDER or not NAV_PLACEHOLDER.strip(): # NAV_PLACEHOLDER.strip() 确保它不只是空格
        print(f"严重错误: 脚本中的 NAV_PLACEHOLDER 变量为空或仅包含空格。值为: '{NAV_PLACEHOLDER}'")
        return

    # 替换占位符
    if NAV_PLACEHOLDER not in index_content_original:
        print(f"错误: 在 '{index_html_path}' 中未找到占位符 '{NAV_PLACEHOLDER}'。")
        print(f"请确保 index.html 文件中包含该占位符: {NAV_PLACEHOLDER}")
        return

    # 执行替换
    # 使用 partition 来分割字符串
    before_placeholder, placeholder_found, after_placeholder = index_content_original.partition(NAV_PLACEHOLDER)
    
    # 确保占位符确实被找到了 (partition 总是返回3个部分，但如果没找到，placeholder_found 会是空)
    # 不过，前面的 `NAV_PLACEHOLDER not in index_content_original` 已经处理了未找到的情况。
    if placeholder_found != NAV_PLACEHOLDER : # 进一步确认 partition 是否按预期工作
         # 这个情况理论上不应该发生，因为 if NAV_PLACEHOLDER not in index_content_original 已经检查过了
         print(f"警告: partition 未能按预期分割字符串，或者占位符 '{NAV_PLACEHOLDER}' 在文件中存在但 partition 行为异常。")
         # 可以考虑在此处返回错误或记录更详细的调试信息
         # return # 如果严格要求，可以在此返回

    new_index_content = before_placeholder + nav_content + after_placeholder
    
    # 只有当内容实际发生变化时才写入文件
    if new_index_content != index_content_original:
        try:
            with open(index_html_path, 'w', encoding='utf-8') as file:
                file.write(new_index_content)
            print(f"'{index_html_path}' 更新成功。")
        except Exception as e:
            print(f"写入 '{index_html_path}' 时发生错误: {e}")
    else:
        print(f"'{index_html_path}' 内容无变化，无需更新。")

if __name__ == '__main__':
    main()
