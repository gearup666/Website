import os
import glob
from bs4 import BeautifulSoup

CARD_TEMPLATE = """
<a href="{link_path}" class="card">
    <h2 class="card-title">{title}</h2>
    <p class="card-description">{description}</p>
</a>
"""

# 必须与 index.html 里的占位符注释块一模一样，包括换行和空格
NAV_PLACEHOLDER = """<!-- 示例卡片结构 (将被脚本替换):
<a href="path/to/your_file.html" class="card">
    <h2 class="card-title">示例文件名</h2>
    <p class="card-description">这是从 meta 标签或 title 标签提取的描述信息。</p>
</a>
-->"""

def extract_details(html_filepath):
    page_title = os.path.splitext(os.path.basename(html_filepath))[0].replace('_', ' ').replace('-', ' ').title()
    description = "暂无描述。"
    try:
        with open(html_filepath, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            title_tag = soup.title
            if title_tag and title_tag.string:
                page_title = title_tag.string.strip()
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_desc_tag and meta_desc_tag.get('content'):
                description = meta_desc_tag.get('content').strip()
            elif page_title != os.path.splitext(os.path.basename(html_filepath))[0].replace('_', ' ').replace('-', ' ').title():
                description = page_title
    except Exception as e:
        print(f"处理文件 '{html_filepath}' 时发生错误: {e}")
    return page_title, description

def main():
    print("开始生成导航链接...")
    base_dir = os.getcwd()
    all_cards_html = []
    excluded_dirs = {'.git', '.github', 'venv', 'node_modules'}
    for filepath_absolute in glob.glob(os.path.join(base_dir, '**', '*.html'), recursive=True):
        relative_filepath = os.path.relpath(filepath_absolute, base_dir)
        path_parts = relative_filepath.split(os.sep)
        if any(part in excluded_dirs for part in path_parts):
            continue
        if os.path.basename(relative_filepath).lower() == 'index.html':
            continue
        print(f"找到文件: {relative_filepath}")
        title, desc = extract_details(filepath_absolute)
        link_path = relative_filepath.replace(os.sep, '/')
        card_html = CARD_TEMPLATE.format(link_path=link_path, title=title, description=desc)
        all_cards_html.append(card_html)
    nav_content = "\n".join(all_cards_html) if all_cards_html else ""
    index_html_path = os.path.join(base_dir, 'index.html')
    try:
        with open(index_html_path, 'r', encoding='utf-8') as file:
            index_content_original = file.read()
    except FileNotFoundError:
        print(f"错误: 导航文件 '{index_html_path}' 未找到。请确保它存在于仓库根目录。")
        return
    if not NAV_PLACEHOLDER or not NAV_PLACEHOLDER.strip():
        print(f"严重错误: 脚本中的 NAV_PLACEHOLDER 变量为空或仅包含空格。值为: '{NAV_PLACEHOLDER}'")
        return
    if NAV_PLACEHOLDER not in index_content_original:
        print(f"错误: 在 '{index_html_path}' 中未找到占位符 '{NAV_PLACEHOLDER}'。")
        print(f"请确保 index.html 文件中包含该占位符: {NAV_PLACEHOLDER}")
        return

    # 增量更新：每次都保留占位符在卡片内容后面，便于下次继续替换
    before, found, after = index_content_original.partition(NAV_PLACEHOLDER)
    new_cards_with_placeholder = nav_content + "\n" + NAV_PLACEHOLDER
    new_index_content = before + new_cards_with_placeholder + after

    # 避免多次插入导致有多个占位符，去除旧卡片和占位符
    # 只保留第一个 NAV_PLACEHOLDER，其它都去掉（防止重复）
    while new_index_content.count(NAV_PLACEHOLDER) > 1:
        first, _, tail = new_index_content.partition(NAV_PLACEHOLDER)
        # 把 tail 里的第一个 NAV_PLACEHOLDER删除
        tail = tail.replace(NAV_PLACEHOLDER, '', 1)
        new_index_content = first + NAV_PLACEHOLDER + tail

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
