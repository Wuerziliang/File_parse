# 导入必要的库和模块
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    CSVLoader,
    PyPDFLoader,
    TextLoader,
    JSONLoader,
    DirectoryLoader,
    UnstructuredFileLoader,
    Docx2txtLoader,  # 添加新的docx加载器
)
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import threading
import _thread
from tqdm import tqdm

# 定义超时异常类和处理器
class TimeoutException(Exception):
    """用于处理文档加载超时的自定义异常类"""
    pass

def timeout_handler():
    """超时处理函数，通过中断主线程来处理超时情况"""
    _thread.interrupt_main()

# 主要的文档处理类
class DocumentProcessor:
    """
    文档处理器类，用于批量处理不同格式的文档文件
    支持格式：PDF, TXT, CSV, DOC, DOCX, JSON
    """
    def __init__(self, input_dir: str, output_dir: str):
        """
        初始化文档处理器
        Args:
            input_dir: 输入文件目录路径
            output_dir: 输出文件目录路径
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.supported_formats = {
            'pdf': PyPDFLoader,
            'txt': TextLoader,
            'csv': CSVLoader,
            'doc': UnstructuredWordDocumentLoader,
            'docx': Docx2txtLoader,
            'json': lambda path: JSONLoader(path, jq_schema='.', text_content=False)
        }

    def create_output_dirs(self):
        """
        创建输出目录结构
        为每种支持的文件格式创建对应的输出子目录
        """
        for format_type in self.supported_formats.keys():
            format_dir = os.path.join(self.output_dir, format_type)
            os.makedirs(format_dir, exist_ok=True)

    def process_file(self, file_path: str) -> Dict[str, Any]:
        file_ext = file_path.split('.')[-1].lower()
        if file_ext not in self.supported_formats:
            return None

        try:
            timer = threading.Timer(60, timeout_handler)
            timer.start()
            
            loader = self.supported_formats[file_ext](file_path)
            documents = loader.load()
            
            timer.cancel()
            return {
                'content': documents,
                'file_type': file_ext,
                'original_path': file_path
            }
        except KeyboardInterrupt:
            print(f"处理文件 {file_path} 超时（超过60秒）")
            return None
        except Exception as e:
            print(f"处理文件 {file_path} 时出错:")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            print(f"文件大小: {os.path.getsize(file_path) / 1024:.2f} KB")
            return None
        finally:
            if 'timer' in locals():
                timer.cancel()

    def process_directory(self):
        """
        处理整个目录下的文件
        功能：
        1. 创建输出目录结构
        2. 扫描并筛选支持的文件
        3. 使用进度条显示处理进度
        4. 统计处理结果（成功/失败/跳过的文件数）
        """
        self.create_output_dirs()
        
        # 首先过滤出支持的文件
        supported_files = []
        total_files = 0
        processed_files = set()  # 添加集合来追踪已处理的文件
        
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                total_files += 1
                file_path = os.path.join(root, file)
                file_ext = file_path.split('.')[-1].lower()
                if file_ext in self.supported_formats:
                    supported_files.append((root, file))

        success_count = 0
        failed_count = 0
        
        # 使用tqdm创建进度条，只处理支持的文件
        with tqdm(total=len(supported_files), desc="处理文件") as pbar:
            for root, file in supported_files:
                file_path = os.path.join(root, file)
                processed_files.add(file_path)  # 记录处理过的文件
                pbar.set_postfix_str(f"正在处理: {file}")
                result = self.process_file(file_path)
                if result and self.save_result(result):  # 修改判断条件
                    success_count += 1
                else:
                    failed_count += 1
                pbar.update(1)
        
        skipped_count = total_files - len(processed_files)  # 修改跳过文件的计算方式
        
        print(f"\n处理完成：")
        print(f"总文件数：{total_files}")
        print(f"成功：{success_count}")
        print(f"失败：{failed_count}")
        print(f"跳过：{skipped_count}")

    def save_result(self, result: Dict[str, Any]) -> bool:
        """
        保存处理结果到JSON文件
        Args:
            result: 包含处理结果的字典
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        if not result:
            return False

        try:
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
            return True
        except Exception as e:
            print(f"保存结果时出错: {str(e)}")
            return False

# 主函数
def main():
    """
    主程序入口
    设置输入输出目录并启动文档处理
    """
    input_directory = "d:\\project\\data_clean\\input"  # 输入目录
    output_directory = "d:\\project\\data_clean\\output"  # 输出目录
    
    processor = DocumentProcessor(input_directory, output_directory)
    processor.process_directory()

if __name__ == "__main__":
    main()
    