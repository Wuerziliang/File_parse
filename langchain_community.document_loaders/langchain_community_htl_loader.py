from langchain_community.document_loaders import BSHTMLLoader
from typing import List, Dict, Any
import os

class HTMLProcessor:
    def __init__(self, input_dir: str):
        self.input_dir = input_dir
        self.supported_extensions = ['.html', '.htm']
    
    def _is_supported_file(self, filename: str) -> bool:
        """检查文件是否为支持的HTML格式"""
        return any(filename.lower().endswith(ext) for ext in self.supported_extensions)
    
    def _process_single_file(self, file_path: str) -> Dict[str, Any]:
        """处理单个HTML文件"""
        try:
            # 尝试不同编码读取文件
            html_content = self._read_file_with_encoding(file_path)
            
            # 创建临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.html', mode='w', encoding='utf-8', delete=False) as temp:
                temp.write(html_content)
                temp_path = temp.name
            
            try:
                # 使用临时文件创建BSHTMLLoader
                loader = BSHTMLLoader(temp_path)
                documents = loader.load()
                
                return {
                    'file_path': file_path,
                    'success': True,
                    'content': documents,
                    'error': None
                }
            finally:
                # 删除临时文件
                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            return {
                'file_path': file_path,
                'success': False,
                'content': None,
                'error': str(e)
            }
    
    def _read_file_with_encoding(self, file_path: str) -> str:
        """尝试不同编码读取文件"""
        encodings = ['utf-8', 'gbk', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
                
        # 如果所有编码都失败，使用二进制模式读取并尝试检测编码
        import chardet
        with open(file_path, 'rb') as f:
            content = f.read()
            detected = chardet.detect(content)
            
        try:
            return content.decode(detected['encoding'])
        except:
            # 最后的尝试：使用 latin-1 编码（它可以解码任何字节序列）
            return content.decode('latin-1')
    
    def process_directory(self) -> List[Dict[str, Any]]:
        """处理目录中的所有HTML文件"""
        results = []
        
        for root, _, files in os.walk(self.input_dir):
            html_files = [f for f in files if self._is_supported_file(f)]
            
            for file in html_files:
                file_path = os.path.join(root, file)
                print(f"正在处理: {file}")
                result = self._process_single_file(file_path)
                results.append(result)
                
                if result['success']:
                    print(f"成功处理文件: {file}")
                    for doc in result['content']:
                        print(f"- 提取的文本长度: {len(doc.page_content)} 字符")
                        print(f"- 元数据: {doc.metadata}")
                else:
                    print(f"处理失败: {file}, 错误: {result['error']}")
                print("-" * 50)
        
        return results

def main():
    input_dir = "d:\\project\\data_clean\\input"
    processor = HTMLProcessor(input_dir)
    results = processor.process_directory()
    
    # 输出统计信息
    success_count = sum(1 for r in results if r['success'])
    print(f"\n处理完成:")
    print(f"总文件数: {len(results)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(results) - success_count}")

if __name__ == "__main__":
    main()