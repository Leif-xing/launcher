"""程序启动工具模块"""
import subprocess
import os
import sys
from typing import Optional


class Launcher:
    """程序启动器"""
    
    @staticmethod
    def launch(path: str, workdir: Optional[str] = None) -> bool:
        """
        启动程序或脚本
        
        Args:
            path: 程序路径或命令
            workdir: 工作目录（可选）
            
        Returns:
            是否启动成功
            
        Raises:
            FileNotFoundError: 文件不存在
            PermissionError: 没有执行权限
            Exception: 其他启动错误
        """
        # 如果没有指定工作目录，使用程序所在目录
        if not workdir:
            if os.path.isfile(path):
                workdir = os.path.dirname(path) or os.getcwd()
            else:
                workdir = os.getcwd()
        
        # 判断文件类型并执行
        print(f"[DEBUG] 启动文件: {path}")
        print(f"[DEBUG] 工作目录: {workdir}")
        print(f"[DEBUG] 文件类型: {os.path.splitext(path)[1]}")
        
        if path.endswith('.py'):
            # Python 脚本
            print(f"[DEBUG] 识别为 Python 脚本")
            subprocess.Popen(
                [sys.executable, path],
                cwd=workdir,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
        elif path.endswith(('.bat', '.cmd')):
            # 批处理脚本
            print(f"[DEBUG] 识别为批处理脚本")
            # 规范化路径为系统分隔符（Windows下为反斜杠）
            path = os.path.normpath(path)
            script_name = os.path.basename(path)
            
            # 使用 shell=True 并手动构建命令字符串，以避免 subprocess 自动转义引号的问题
            # start "Title" /max cmd.exe /k "path_to_script"
            cmd_command = f'start "{script_name}" /max cmd.exe /k "{path}"'
            print(f"[DEBUG] 执行命令: {cmd_command}")
            
            subprocess.Popen(
                cmd_command,
                cwd=workdir,
                shell=True
            )
        elif path.endswith('.lnk'):
            # 快捷方式
            print(f"[DEBUG] 识别为快捷方式")
            if sys.platform == 'win32':
                os.startfile(path)
            else:
                # 非 Windows 平台通常不支持 .lnk，尝试用默认方式
                subprocess.Popen(['xdg-open', path])
        elif path.endswith('.exe') or not os.path.splitext(path)[1]:
            # 可执行文件或系统命令
            print(f"[DEBUG] 识别为可执行文件或系统命令")
            subprocess.Popen(
                path,
                cwd=workdir,
                shell=True
            )
        else:
            # 其他类型，尝试用系统默认方式打开
            print(f"[DEBUG] 使用系统默认方式打开")
            if sys.platform == 'win32':
                os.startfile(path)
            else:
                subprocess.Popen(['xdg-open', path])
        
        print(f"[DEBUG] 启动命令已执行")
        return True
    
    @staticmethod
    def validate_path(path: str) -> tuple[bool, str]:
        """
        验证路径是否有效
        
        Args:
            path: 待验证的路径
            
        Returns:
            (是否有效, 错误信息)
        """
        if not path:
            return False, "路径不能为空"
        
        # 如果是系统命令（不带路径分隔符），认为有效
        if os.sep not in path and '/' not in path:
            return True, ""
        
        # 检查文件是否存在
        if not os.path.exists(path):
            return False, f"文件不存在: {path}"
        
        return True, ""
