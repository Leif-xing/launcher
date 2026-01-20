"""备份管理对话框"""
import customtkinter as ctk
from typing import Optional, List, Dict


class BackupDialog(ctk.CTkToplevel):
    """备份管理对话框"""
    
    def __init__(self, parent, backups: List[Dict]):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            backups: 备份文件列表
        """
        super().__init__(parent)
        
        self.result = None
        self.backups = backups
        self.selected_index = -1
        
        # 设置窗口
        self.title("备份管理")
        self.geometry("600x450")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets()
        
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
    
    def _create_widgets(self):
        """创建对话框组件"""
        # 主容器
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="配置文件备份列表",
            font=("Microsoft YaHei UI", 14, "bold")
        )
        title_label.pack(fill="x", pady=(0, 10))
        
        # 备份列表容器
        list_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=("#2b2b2b", "#2b2b2b"),
            corner_radius=8
        )
        list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # 创建备份列表
        self.backup_frames = []
        if not self.backups:
            # 无备份提示
            empty_label = ctk.CTkLabel(
                list_frame,
                text="暂无备份文件",
                text_color=("#666666", "#666666"),
                font=("Microsoft YaHei UI", 12)
            )
            empty_label.pack(expand=True, pady=30)
        else:
            for i, backup in enumerate(self.backups):
                self._create_backup_item(list_frame, i, backup)
        
        # 按钮区域
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # 关闭按钮
        close_btn = ctk.CTkButton(
            button_frame,
            text="关闭",
            width=100,
            height=35,
            command=self._on_close
        )
        close_btn.pack(side="right")
        
        # 恢复按钮
        self.restore_btn = ctk.CTkButton(
            button_frame,
            text="恢复此备份",
            width=120,
            height=35,
            state="disabled",
            command=self._on_restore
        )
        self.restore_btn.pack(side="right", padx=(0, 10))
        
        # 绑定 ESC 键
        self.bind("<Escape>", lambda e: self._on_close())
    
    def _create_backup_item(self, parent, index: int, backup: Dict):
        """创建备份项"""
        # 备份项容器
        item_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=6
        )
        item_frame.pack(fill="x", padx=5, pady=3)
        
        # 备份按钮
        item_btn = ctk.CTkButton(
            item_frame,
            text="",
            height=60,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            anchor="w",
            command=lambda: self._select_backup(index)
        )
        item_btn.pack(fill="both", expand=True)
        
        # 备份信息文本
        info_text = f"📁 {backup['filename']}\n" \
                   f"   时间: {backup['timestamp']}  |  大小: {self._format_size(backup['size'])}"
        
        info_label = ctk.CTkLabel(
            item_btn,
            text=info_text,
            font=("Microsoft YaHei UI", 10),
            text_color=("#e0e0e0", "#e0e0e0"),
            anchor="w",
            justify="left"
        )
        info_label.place(relx=0.02, rely=0.5, anchor="w")
        
        self.backup_frames.append(item_btn)
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def _select_backup(self, index: int):
        """选择备份"""
        # 取消之前的选中
        for btn in self.backup_frames:
            btn.configure(fg_color="transparent")
        
        # 选中当前项
        if 0 <= index < len(self.backup_frames):
            self.backup_frames[index].configure(fg_color=("#4a9eff", "#4a9eff"))
            self.selected_index = index
            self.restore_btn.configure(state="normal")
    
    def _on_restore(self):
        """恢复备份"""
        if 0 <= self.selected_index < len(self.backups):
            self.result = self.backups[self.selected_index]["filepath"]
            self.grab_release()
            self.destroy()
    
    def _on_close(self):
        """关闭对话框"""
        self.result = None
        self.grab_release()
        self.destroy()
    
    def show(self) -> Optional[str]:
        """
        显示对话框并等待结果
        
        Returns:
            选中的备份文件路径，未选择返回 None
        """
        self.wait_window()
        return self.result
