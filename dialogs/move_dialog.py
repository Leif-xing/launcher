"""移动到分类对话框"""
import customtkinter as ctk
from typing import Optional, List


class MoveDialog(ctk.CTkToplevel):
    """移动到分类对话框"""
    
    def __init__(self, parent, categories: List[str], current_category: str):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            categories: 可选分类列表（已排除当前分类）
            current_category: 当前分类名称
        """
        super().__init__(parent)
        
        self.result = None
        self.categories = categories
        self.current_category = current_category
        self.selected_index = 0
        
        # 设置窗口
        self.title("移动到")
        
        # 根据分类数量动态调整高度
        list_height = min(len(categories) * 35 + 10, 300)
        window_height = list_height + 140
        self.geometry(f"350x{window_height}")
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
        
        # 提示文本
        hint_label = ctk.CTkLabel(
            main_frame,
            text=f"选择目标分类（当前: {self.current_category}）",
            font=("Microsoft YaHei UI", 11),
            text_color=("#888888", "#888888")
        )
        hint_label.pack(fill="x", pady=(0, 10))
        
        # 分类列表框
        list_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=("#2b2b2b", "#2b2b2b"),
            corner_radius=8
        )
        list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # 创建分类按钮
        self.category_buttons = []
        for i, category in enumerate(self.categories):
            btn = ctk.CTkButton(
                list_frame,
                text=category,
                height=32,
                fg_color="transparent",
                hover_color=("#3a3a3a", "#3a3a3a"),
                anchor="w",
                command=lambda idx=i: self._select_category(idx)
            )
            btn.pack(fill="x", padx=5, pady=2)
            self.category_buttons.append(btn)
        
        # 如果没有可用分类
        if not self.categories:
            empty_label = ctk.CTkLabel(
                list_frame,
                text="没有其他可用分类",
                text_color=("#666666", "#666666")
            )
            empty_label.pack(expand=True, pady=20)
        else:
            # 默认选中第一个
            self._select_category(0)
        
        # 按钮区域
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="取消",
            width=100,
            height=35,
            fg_color=("#666666", "#666666"),
            hover_color=("#555555", "#555555"),
            command=self._on_cancel
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        ok_btn = ctk.CTkButton(
            button_frame,
            text="确定",
            width=100,
            height=35,
            command=self._on_ok
        )
        ok_btn.pack(side="right")
        
        # 绑定键盘事件
        self.bind("<Escape>", lambda e: self._on_cancel())
        self.bind("<Return>", lambda e: self._on_ok())
        self.bind("<Up>", lambda e: self._navigate(-1))
        self.bind("<Down>", lambda e: self._navigate(1))
    
    def _select_category(self, index: int):
        """选中分类"""
        if 0 <= index < len(self.categories):
            # 取消之前的选中状态
            for btn in self.category_buttons:
                btn.configure(fg_color="transparent")
            
            # 选中当前项
            self.category_buttons[index].configure(fg_color=("#4a9eff", "#4a9eff"))
            self.selected_index = index
    
    def _navigate(self, direction: int):
        """键盘导航"""
        if not self.categories:
            return
        
        new_index = (self.selected_index + direction) % len(self.categories)
        self._select_category(new_index)
    
    def _on_ok(self):
        """确定按钮"""
        if not self.categories:
            return
        
        self.result = self.categories[self.selected_index]
        self.grab_release()
        self.destroy()
    
    def _on_cancel(self):
        """取消按钮"""
        self.result = None
        self.grab_release()
        self.destroy()
    
    def show(self) -> Optional[str]:
        """
        显示对话框并等待结果
        
        Returns:
            选中的分类名称，取消返回 None
        """
        self.wait_window()
        return self.result
