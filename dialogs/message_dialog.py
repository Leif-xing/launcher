"""消息对话框模块"""
import customtkinter as ctk
from typing import Optional


class MessageDialog(ctk.CTkToplevel):
    """消息对话框"""
    
    def __init__(self, parent, title: str, message: str, dialog_type: str = "info"):
        """
        初始化消息对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 消息内容
            dialog_type: 对话框类型 (info, error, warning, question)
        """
        super().__init__(parent)
        
        self.title(title)
        self.result = None
        
        # 设置窗口属性
        if dialog_type == "question":
            self.geometry("380x180")
        else:
            self.geometry("380x160")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets(message, dialog_type)
        
        # 抓取焦点
        self.grab_set()
        self.focus_set()
    
    def _center_window(self):
        """窗口居中"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self, message: str, dialog_type: str):
        """创建对话框组件"""
        # 图标和消息区域
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(15, 10))
        
        # 图标
        icon_map = {
            "info": "ℹ️",
            "error": "❌",
            "warning": "⚠️",
            "question": "❓"
        }
        icon = icon_map.get(dialog_type, "ℹ️")
        
        icon_label = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=("Segoe UI Emoji", 28)
        )
        icon_label.pack(pady=(5, 8))
        
        # 消息文本
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=("Microsoft YaHei UI", 11),
            wraplength=330,
            justify="center"
        )
        message_label.pack(pady=(0, 10))
        
        # 按钮区域
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        if dialog_type == "question":
            # 是/否按钮
            no_btn = ctk.CTkButton(
                button_frame,
                text="否",
                width=100,
                command=self._on_no
            )
            no_btn.pack(side="right", padx=(10, 0))
            
            yes_btn = ctk.CTkButton(
                button_frame,
                text="是",
                width=100,
                command=self._on_yes
            )
            yes_btn.pack(side="right")
        else:
            # 确定按钮
            ok_btn = ctk.CTkButton(
                button_frame,
                text="确定",
                width=100,
                command=self._on_ok
            )
            ok_btn.pack(side="right")
        
        # 绑定 ESC 键关闭
        self.bind("<Escape>", lambda e: self._on_ok())
    
    def _on_ok(self):
        """确定按钮"""
        self.result = True
        self.grab_release()
        self.destroy()
    
    def _on_yes(self):
        """是按钮"""
        self.result = True
        self.grab_release()
        self.destroy()
    
    def _on_no(self):
        """否按钮"""
        self.result = False
        self.grab_release()
        self.destroy()
    
    def show(self) -> Optional[bool]:
        """
        显示对话框并等待结果
        
        Returns:
            用户选择结果
        """
        self.wait_window()
        return self.result


def show_info(parent, title: str, message: str):
    """显示信息对话框"""
    dialog = MessageDialog(parent, title, message, "info")
    dialog.show()


def show_error(parent, title: str, message: str):
    """显示错误对话框"""
    dialog = MessageDialog(parent, title, message, "error")
    dialog.show()


def show_warning(parent, title: str, message: str):
    """显示警告对话框"""
    dialog = MessageDialog(parent, title, message, "warning")
    dialog.show()


def show_question(parent, title: str, message: str) -> bool:
    """
    显示询问对话框
    
    Returns:
        True: 用户点击"是"
        False: 用户点击"否"
    """
    dialog = MessageDialog(parent, title, message, "question")
    return dialog.show() or False
