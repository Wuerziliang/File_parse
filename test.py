import psutil
import os
from datetime import datetime

def format_bytes(bytes):
    """格式化字节大小为GB，保留2位小数"""
    return f"{bytes / (1024 * 1024 * 1024):.2f}"

def get_system_info():
    try:
        print("\n=== 系统信息监控 ===")
        print(f"检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # CPU信息
        print("\n[CPU信息]")
        print(f"CPU核心数: {psutil.cpu_count()} 核")
        print(f"物理核心数: {psutil.cpu_count(logical=False)} 核")
        print(f"CPU使用率: {psutil.cpu_percent(interval=1)}%")
        
        # 内存信息
        print("\n[内存信息]")
        memory = psutil.virtual_memory()
        print(f"总内存: {format_bytes(memory.total)} GB")
        print(f"可用内存: {format_bytes(memory.available)} GB")
        print(f"已用内存: {format_bytes(memory.used)} GB")
        print(f"内存使用率: {memory.percent}%")
        
        # 硬盘信息
        print("\n[硬盘信息]")
        for partition in psutil.disk_partitions():
            try:
                if os.name == 'nt':  # Windows系统
                    if 'cdrom' in partition.opts or partition.fstype == '':
                        continue  # 跳过光驱和特殊分区
                usage = psutil.disk_usage(partition.mountpoint)
                print(f"\n磁盘 {partition.mountpoint}")
                print(f"总空间: {format_bytes(usage.total)} GB")
                print(f"已用空间: {format_bytes(usage.used)} GB")
                print(f"可用空间: {format_bytes(usage.free)} GB")
                print(f"使用率: {usage.percent}%")
            except Exception as e:
                print(f"无法访问磁盘 {partition.mountpoint}: {str(e)}")
        
        # GPU信息（使用PyTorch替代tensorflow）
        try:
            import torch
            print("\n[GPU信息]")
            if torch.cuda.is_available():
                print(f"CUDA是否可用: 是")
                print(f"GPU数量: {torch.cuda.device_count()}")
                for i in range(torch.cuda.device_count()):
                    print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
                print(f"当前GPU: {torch.cuda.current_device()}")
                print(f"CUDA版本: {torch.version.cuda}")
            else:
                print("[GPU信息] 未检测到可用的GPU")
        except ImportError:
            print("\n[GPU信息] 未安装PyTorch，无法检测GPU信息")
        
        # 网络信息
        print("\n[网络信息]")
        net_io = psutil.net_io_counters()
        print(f"发送: {format_bytes(net_io.bytes_sent)} GB")
        print(f"接收: {format_bytes(net_io.bytes_recv)} GB")
        
    except Exception as e:
        print(f"获取系统信息时出错: {str(e)}")

if __name__ == "__main__":
    get_system_info()
