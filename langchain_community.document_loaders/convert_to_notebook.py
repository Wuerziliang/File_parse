import nbformat as nbf
import os

# 设置文件路径
base_dir = r"d:\project\data_clean\langchain_community.document_loaders"
input_file = os.path.join(base_dir, "langchain_community.document_loaders_v2.py")
output_file = os.path.join(base_dir, "langchain_community.document_loaders_v2.ipynb")

# 创建新的 notebook
nb = nbf.v4.new_notebook()

# 添加单元格
cells = [
    # 标题说明
    nbf.v4.new_markdown_cell("""# 文档处理器
用于批量处理不同格式的文档，支持：
- PDF, TXT, CSV, DOC, DOCX, JSON 文件
- ZIP, 7Z 压缩包"""),
    
    # 导入模块
    nbf.v4.new_markdown_cell("## 导入必要的模块"),
    nbf.v4.new_code_cell("""from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader, CSVLoader, PyPDFLoader,
    TextLoader, JSONLoader, Docx2txtLoader,
)
import os, json, zipfile, tempfile
import py7zr
from datetime import datetime
from typing import Dict, Any, List
import threading, _thread
from tqdm import tqdm"""),

    # 类定义（包含所有方法）
    nbf.v4.new_markdown_cell("## DocumentProcessor 类定义"),
    nbf.v4.new_code_cell("""class DocumentProcessor:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.supported_formats = {
            'pdf': PyPDFLoader, 'txt': TextLoader, 'csv': CSVLoader,
            'doc': UnstructuredWordDocumentLoader, 'docx': Docx2txtLoader,
            'json': lambda path: JSONLoader(path, jq_schema='.', text_content=False)
        }
        [os.makedirs(os.path.join(output_dir, fmt), exist_ok=True) 
         for fmt in {**self.supported_formats, 'zip': None, '7z': None}]

    def process_file(self, file_path: str) -> Dict[str, Any]:
        file_ext = file_path.split('.')[-1].lower()
        
        if file_ext in ['zip', '7z']:
            results = []
            with tempfile.TemporaryDirectory() as temp_dir:
                if file_ext == 'zip':
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                else:  # 7z
                    with py7zr.SevenZipFile(file_path, 'r') as sz_ref:
                        sz_ref.extractall(temp_dir)
                        
                for root, _, files in os.walk(temp_dir):
                    results.extend([
                        result for file in files 
                        if (result := self.process_file(os.path.join(root, file)))
                    ])
            return {'content': results, 'file_type': file_ext, 'original_path': file_path}
        
        if file_ext not in self.supported_formats:
            return None

        try:
            timer = threading.Timer(120, _thread.interrupt_main)
            timer.start()
            try:
                loader = self.supported_formats[file_ext](file_path)
                documents = loader.load()
                return {
                    'content': documents,
                    'file_type': file_ext,
                    'original_path': file_path
                }
            finally:
                timer.cancel()
        except Exception as e:
            print(f"处理文件 {file_path} 失败: {type(e).__name__} - {str(e)}")
            print(f"文件大小: {os.path.getsize(file_path) / 1024:.2f} KB")
            return None

    def save_result(self, result: Dict[str, Any]) -> bool:
        if not result:
            return False
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                self.output_dir, result['file_type'],
                f"{os.path.basename(result['original_path'])}_{timestamp}.json"
            )
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'original_file': result['original_path'],
                    'processed_time': timestamp,
                    'documents': [{
                        'content': doc.page_content,
                        'metadata': doc.metadata
                    } for doc in result['content']]
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存结果时出错: {str(e)}")
            return False

    def process_directory(self):
        supported_files = [
            (root, file) for root, _, files in os.walk(self.input_dir)
            for file in files 
            if file.split('.')[-1].lower() in {**self.supported_formats, 'zip': None, '7z': None}
        ]
        total_files = sum(1 for _ in os.walk(self.input_dir) for _ in _[2])
        success_count = failed_count = 0
        
        with tqdm(total=len(supported_files), desc="处理文件") as pbar:
            for root, file in supported_files:
                file_path = os.path.join(root, file)
                pbar.set_postfix_str(f"正在处理: {file}")
                
                if result := self.process_file(file_path):
                    if isinstance(result['content'], list) and all(isinstance(x, dict) for x in result['content']):
                        success_count += sum(bool(self.save_result(zip_result)) for zip_result in result['content'])
                    else:
                        success_count += bool(self.save_result(result))
                else:
                    failed_count += 1
                pbar.update(1)
        
        print(f"\\n处理完成：")
        print(f"总文件数：{total_files}")
        print(f"成功：{success_count}")
        print(f"失败：{failed_count}")
        print(f"跳过：{total_files - len(supported_files)}")"""),

    # 使用示例
    nbf.v4.new_markdown_cell("## 使用示例"),
    nbf.v4.new_code_cell("""processor = DocumentProcessor(
    "d:\\\\project\\\\data_clean\\\\input",
    "d:\\\\project\\\\data_clean\\\\output"
)
processor.process_directory()""")
]

# 组装 notebook
nb['cells'] = cells

# 保存为 .ipynb 文件
with open(output_file, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)