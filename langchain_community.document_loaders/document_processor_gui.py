import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader, CSVLoader, PyPDFLoader,
    TextLoader, JSONLoader, BSHTMLLoader
)
import os, json
from datetime import datetime
from typing import Dict, Any
from tqdm import tqdm

class DocumentProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文档处理工具")
        self.root.geometry("800x600")
        
        # 支持的文件格式
        self.supported_formats = {
            'pdf': PyPDFLoader, 'txt': TextLoader, 'csv': CSVLoader,
            'doc': UnstructuredWordDocumentLoader, 'docx': UnstructuredWordDocumentLoader,
            'json': JSONLoader, 'html': BSHTMLLoader, 'htm': BSHTMLLoader
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        # 输入输出路径框架
        path_frame = ttk.LabelFrame(self.root, text="路径设置", padding=10)
        path_frame.pack(fill="x", padx=10, pady=5)
        
        # 输入路径
        ttk.Label(path_frame, text="输入目录:").grid(row=0, column=0, sticky="w")
        self.input_path = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(path_frame, text="浏览", command=self.browse_input).grid(row=0, column=2)
        
        # 输出路径
        ttk.Label(path_frame, text="输出目录:").grid(row=1, column=0, sticky="w")
        self.output_path = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(path_frame, text="浏览", command=self.browse_output).grid(row=1, column=2)
        
        # 进度显示
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress.pack(fill="x", padx=10, pady=5)
        
        # 日志显示
        log_frame = ttk.LabelFrame(self.root, text="处理日志", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=20)
        self.log_text.pack(fill="both", expand=True)
        
        # 控制按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="开始处理", command=self.start_processing).pack(side="left", padx=5)
        ttk.Button(button_frame, text="清空日志", command=self.clear_log).pack(side="left", padx=5)
        
    def browse_input(self):
        path = filedialog.askdirectory()
        if path:
            self.input_path.set(path)
            
    def browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path.set(path)
            
    def log(self, message):
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.root.update()
        
    def clear_log(self):
        self.log_text.delete(1.0, "end")
        
    def start_processing(self):
        input_dir = self.input_path.get()
        output_dir = self.output_path.get()
        
        if not input_dir or not output_dir:
            messagebox.showerror("错误", "请选择输入和输出目录")
            return
            
        processor = DocumentProcessor(input_dir, output_dir, self.log, self.progress_var)
        processor.process_directory()

class DocumentProcessor:
    def __init__(self, input_dir, output_dir, log_func, progress_var):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.log = log_func
        self.progress_var = progress_var
        self.supported_formats = {
            'pdf': PyPDFLoader, 'txt': TextLoader, 'csv': CSVLoader,
            'doc': UnstructuredWordDocumentLoader, 'docx': UnstructuredWordDocumentLoader,
            'json': JSONLoader, 'html': BSHTMLLoader, 'htm': BSHTMLLoader
        }
        
    # ... 其余方法保持不变，但添加进度更新 ...
    
    def process_directory(self):
        try:
            # 创建输出目录
            for fmt in self.supported_formats:
                os.makedirs(os.path.join(self.output_dir, fmt), exist_ok=True)
            
            # 获取文件列表
            files = [(root, f) for root, _, files in os.walk(self.input_dir) 
                    for f in files if f.split('.')[-1].lower() in self.supported_formats]
            total_files = len(files)
            
            for i, (root, file) in enumerate(files, 1):
                file_path = os.path.join(root, file)
                self.log(f"处理文件 ({i}/{total_files}): {file}")
                
                result = self.process_file(file_path)
                if result:
                    self.save_result(result)
                    self.log(f"成功处理: {file}")
                else:
                    self.log(f"处理失败: {file}")
                    
                # 更新进度
                self.progress_var.set((i / total_files) * 100)
                
            self.log("\n处理完成!")
            messagebox.showinfo("完成", "所有文件处理完成！")
            
        except Exception as e:
            self.log(f"发生错误: {str(e)}")
            messagebox.showerror("错误", f"处理过程中发生错误：{str(e)}")

def main():
    root = tk.Tk()
    app = DocumentProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()