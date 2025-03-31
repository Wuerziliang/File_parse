from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    CSVLoader,
    PyPDFLoader,
    TextLoader,
    JSONLoader,
    BSHTMLLoader,
    DirectoryLoader,
    UnstructuredFileLoader
)
import os
import json
from datetime import datetime
from typing import Dict, List, Any

class DocumentProcessor:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.supported_formats = {
            'pdf': PyPDFLoader,
            'txt': TextLoader,
            'csv': CSVLoader,
            'doc': UnstructuredWordDocumentLoader,
            'docx': UnstructuredWordDocumentLoader,
            'json': JSONLoader,
            'html': BSHTMLLoader,
            'htm': BSHTMLLoader
        }
        
    def create_output_dirs(self):
        """创建输出目录结构"""
        for format_type in self.supported_formats.keys():
            format_dir = os.path.join(self.output_dir, format_type)
            os.makedirs(format_dir, exist_ok=True)

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """处理单个文件"""
        file_ext = file_path.split('.')[-1].lower()
        if file_ext not in self.supported_formats:
            return None

        try:
            loader_class = self.supported_formats[file_ext]
            if file_ext == 'json':
                loader = loader_class(file_path, jq_schema='.', text_content=False)
            elif file_ext in ['html', 'htm']:
                # BSHTMLLoader 不支持直接设置编码，需要先读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                loader = loader_class(html_content)
            else:
                loader = loader_class(file_path)
            
            documents = loader.load()
            return {
                'content': documents,
                'file_type': file_ext,
                'original_path': file_path
            }
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
            return None

    def save_result(self, result: Dict[str, Any]):
        """保存处理结果"""
        if not result:
            return

        file_type = result['file_type']
        original_filename = os.path.basename(result['original_path'])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{original_filename}_{timestamp}.json"
        output_path = os.path.join(self.output_dir, file_type, output_filename)

        output_data = {
            'original_file': result['original_path'],
            'processed_time': timestamp,
            'documents': []
        }

        for doc in result['content']:
            doc_data = {
                'content': doc.page_content,
                'metadata': doc.metadata
            }
            output_data['documents'].append(doc_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

    def process_directory(self):
        """处理整个目录"""
        self.create_output_dirs()
        
        # 获取总文件数
        total_files = sum([len(files) for _, _, files in os.walk(self.input_dir)])
        processed_files = 0
        
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                processed_files += 1
                file_path = os.path.join(root, file)
                print(f"处理进度: {processed_files}/{total_files} - {file}")
                result = self.process_file(file_path)
                if result:
                    self.save_result(result)

def main():
    input_directory = "d:\\project\\data_clean\\input"  # 输入目录
    output_directory = "d:\\project\\data_clean\\output"  # 输出目录
    
    processor = DocumentProcessor(input_directory, output_directory)
    processor.process_directory()

if __name__ == "__main__":
    main()
    