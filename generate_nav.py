# generate_nav.py
import os
import glob
from bs4 import BeautifulSoup # 需要安装: pip install beautifulsoup4

def get_html_details(filepath):
    """
    从 HTML 文件中提取标题和描述。
    优先顺序:
    1. <meta name="description">
    2. <title>
    3. 文件名 (作为标题和描述)
    """
    filename_title = os.path.splitext(os.path.basename(filepath))[0].replace('_', ' ').replace('-', ' ').title()
    description = filename_title # 默认描述为文件名
    page_title = filename_title   # 默认页面标题为文件名

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_desc_tag and meta_desc_tag.get('content'):
                description = meta_desc_tag.get('content').strip()

            title_tag = soup.title
            if title_tag and title_tag.string:
                page_title = title_tag.string.strip()
                # 如果描述仍然是文件名，并且页面标题更具描述性，则使用页面标题作为描述
                if description == filename_title and page_title != filename_title:
                    description = page_title

    except Exception as e:
        print(f"处理文件 {filepath} 时出错: {e}")
        # 出错时，描述和标题将保留为基于文件名的默认值

    return page_title, description

def generate_card_html(file_title, link_path, description):
    """为每个HTML文件生成卡片HTML代码"""
    # 你可以根据第二个文档中的CSS样式自定义这里的HTML结构
    return f"""
<div class="card">
  <h3><a href="{link_path}">{file_title}</a></h3>
  <p>{description}</p>
</div>
"""

def main():
    nav_links_html = ""
    # 查找所有HTML文件，排除index.html自身和.github目录下的文件
    # 假设脚本在仓库根目录运行
    html_files = [
        f for f in glob.glob('**/*.html', recursive=True) 
        if os.path.basename(f).lower() != 'index.html' 
        and not f.startswith(('.github/', 'venv/', 'node_modules/')) # 排除常见目录
    ]

    if not html_files:
        print("未找到用于生成导航的HTML文件 (已排除 index.html)。")

    # 对文件进行排序，可以按文件名或路径
    html_files.sort()

    for filepath in html_files:
        link_path = filepath.replace(os.path.sep, '/') # 确保URL路径使用 /

        # 从文件名获取一个简洁的标题用于卡片标题
        card_main_title = os.path.splitext(os.path.basename(filepath))[0].replace('_', ' ').replace('-', ' ').title()

        # 获取页面的详细标题和描述
        _, file_description = get_html_details(filepath) # page_title_detail 变量未使用，但可以提取出来

        nav_links_html += generate_card_html(card_main_title, link_path, file_description)

    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            index_content = f.read()
    except FileNotFoundError:
        print("错误: 未找到 index.html。请创建一个包含占位符的基础 index.html 文件。")
        return

    placeholder = ""
    if placeholder not in index_content:
        print(f"错误: 在 index.html 中未找到占位符 '{placeholder}'。")
        return

    # 确保占位符前后的内容保持不变，只替换占位符本身
    parts = index_content.split(placeholder)
    if len(parts) == 2:
        new_index_content = parts[0] + nav_links_html + parts[1]
    else:
        print(f"错误: 占位符 '{placeholder}' 在 index.html 中出现多次或结构异常。")
        return

    # 仅当内容发生变化时才写入文件
    if new_index_content != index_content:
        try:
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(new_index_content)
            print("index.html 更新成功。")
        except Exception as e:
            print(f"写入更新后的 index.html 时出错: {e}")
    else:
        print("index.html 内容无变化，无需更新。")

if __name__ == "__main__":
    main()
