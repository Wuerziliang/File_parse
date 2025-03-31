from langchain_community.document_loaders import BSHTMLLoader
from bs4 import BeautifulSoup
from langchain_core.documents import Document

def read_html_file(file_path):
    """尝试不同编码读取HTML文件"""
    encodings = ['utf-8', 'gbk']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"无法使用 {encodings} 编码读取文件")

def parse_html(html_content, file_path):
    """解析HTML内容并返回Document对象"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 获取正文内容
    text = soup.get_text(separator='\n', strip=True)
    
    # 提取元数据
    metadata = {
        'source': file_path,
        'title': soup.title.string if soup.title else '',
        'language': soup.get('lang', ''),
    }
    
    return Document(
        page_content=text,
        metadata=metadata
    )

# 主处理流程
file_path = "D:\\project\\data_clean\\input\\BIT-268001.html"
html_content = read_html_file(file_path)
document = parse_html(html_content, file_path)
print(document)
