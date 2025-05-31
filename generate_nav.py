import os
import glob
from bs4 import BeautifulSoup

# 更新后的卡片模板，只包含标题和图标
# 图标使用了 Font Awesome，需要在 index.html 中引入
CARD_TEMPLATE = """
<a href="{link_path}" class="card group">
    <div class="card-icon">
        <i class="fas fa-file-alt"></i> </div>
    <h2 class="card-title">{title}</h2>
</a>
"""

# 更新后的占位符，更简洁
NAV_PLACEHOLDER = """zhanweifu"""

def extract_title(html_filepath):
    """只提取页面的标题"""
    page_title = os.path.splitext(os.path.basename(html_filepath))[0].replace('_', ' ').replace('-', ' ').title()
    try:
        with open(html_filepath, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            title_tag = soup.title
            if title_tag and title_tag.string:
                page_title = title_tag.string.strip()
    except Exception as e:
        print(f"处理文件 '{html_filepath}' 时发生错误: {e}")
    return page_title

def main():
    print("开始生成导航链接...")
    base_dir = os.getcwd()
    all_cards_html = []
    # 排除常见的无需导航的目录
    excluded_dirs = {'.git', '.github', 'venv', 'node_modules', '__pycache__'}
    # 确保 html_content 目录存在，如果不存在则不进行扫描
    html_content_dir = os.path.join(base_dir, 'html_content')
    if not os.path.isdir(html_content_dir):
        print(f"警告: 'html_content' 目录未找到，将不会扫描其中的HTML文件。")
        # 即使 html_content 不存在，也尝试更新 index.html 中的占位符（如果之前有内容）
        # 或者如果 all_cards_html 为空，则只保留占位符
    else:
        for filepath_absolute in glob.glob(os.path.join(html_content_dir, '**', '*.html'), recursive=True):
            relative_filepath = os.path.relpath(filepath_absolute, base_dir)
            path_parts = relative_filepath.split(os.sep)

            # 检查路径中是否包含任何排除的目录名
            if any(part in excluded_dirs for part in path_parts):
                continue

            # 排除根目录下的 index.html
            if os.path.dirname(relative_filepath) == '' and os.path.basename(relative_filepath).lower() == 'index.html':
                continue
            
            print(f"找到文件: {relative_filepath}")
            title = extract_title(filepath_absolute)
            # 确保链接路径使用斜杠 /
            link_path = relative_filepath.replace(os.sep, '/')
            card_html = CARD_TEMPLATE.format(link_path=link_path, title=title)
            all_cards_html.append(card_html)

    nav_content = "\n".join(all_cards_html) if all_cards_html else ""

    index_html_path = os.path.join(base_dir, 'index.html')
    try:
        with open(index_html_path, 'r', encoding='utf-8') as file:
            index_content_original = file.read()
    except FileNotFoundError:
        print(f"错误: 导航文件 '{index_html_path}' 未找到。请确保它存在于仓库根目录。")
        return

    if not NAV_PLACEHOLDER:
        print(f"严重错误: 脚本中的 NAV_PLACEHOLDER 变量为空。")
        return
        
    # 检查占位符是否存在
    placeholder_start_index = index_content_original.find(NAV_PLACEHOLDER)

    if placeholder_start_index == -1:
        # 如果旧的复杂占位符存在，尝试用旧的占位符进行替换
        # 这部分是为了兼容你之前使用的多行占位符
        OLD_NAV_PLACEHOLDER = """<!-- 示例卡片结构 (将被脚本替换):
<a href="path/to/your_file.html" class="card">
    <h2 class="card-title">示例文件名</h2>
    <p class="card-description">这是从 meta 标签或 title 标签提取的描述信息。</p>
</a>
-->"""
        old_placeholder_start_index = index_content_original.find(OLD_NAV_PLACEHOLDER)
        if old_placeholder_start_index != -1:
            print(f"信息: 在 '{index_html_path}' 中找到旧版占位符，将进行替换。")
            # 构建新的内容，用新占位符替换旧占位符，并在新占位符前插入卡片内容
            # 首先分割出旧占位符之前和之后的部分
            before_old_placeholder = index_content_original[:old_placeholder_start_index]
            after_old_placeholder = index_content_original[old_placeholder_start_index + len(OLD_NAV_PLACEHOLDER):]
            
            # 组合新的内容：旧占位符前的内容 + 生成的卡片 + 新的占位符 + 旧占位符后的内容
            # 确保新卡片内容和新占位符之间有换行
            if nav_content:
                new_index_content = before_old_placeholder + nav_content + "\n" + NAV_PLACEHOLDER + after_old_placeholder
            else: # 如果没有卡片内容，则只替换占位符
                new_index_content = before_old_placeholder + NAV_PLACEHOLDER + after_old_placeholder
        else:
            print(f"错误: 在 '{index_html_path}' 中未找到占位符 '{NAV_PLACEHOLDER}' 或旧版占位符。")
            print(f"请确保 index.html 文件中包含以下占位符之一:\n{NAV_PLACEHOLDER}\n或者旧版的多行占位符。")
            return
    else:
        # 如果找到了新的单行占位符
        # 分割内容，在占位符之前插入卡片内容，然后保留占位符
        before_placeholder = index_content_original[:placeholder_start_index]
        after_placeholder = index_content_original[placeholder_start_index:] # 包含占位符本身及其后的所有内容

        # 确保新卡片内容和占位符之间有换行（如果nav_content不为空）
        if nav_content:
            new_index_content = before_placeholder + nav_content + "\n" + after_placeholder
        else: # 如果没有卡片内容，则内容不变（因为占位符还在）
            new_index_content = index_content_original


    # 写入文件
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
