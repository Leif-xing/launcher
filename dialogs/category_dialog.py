"""分类添加/编辑对话框"""
import customtkinter as ctk
from typing import Optional, List


class CategoryDialog(ctk.CTkToplevel):
    """分类添加/编辑对话框"""
    
    def __init__(self, parent, mode: str = "add", category_name: Optional[str] = None, all_categories: Optional[List[str]] = None):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            mode: 模式 (add: 添加, rename: 重命名, delete: 删除)
            category_name: 分类名称（编辑/删除模式）
            all_categories: 所有分类列表（删除模式）
        """
        super().__init__(parent)
        
        self.result = None
        self.mode = mode
        self.category_name = category_name
        self.all_categories = all_categories or []
        
        # 设置窗口
        titles = {
            "add": "添加分类",
            "rename": "重命名分类",
            "delete": "删除分类"
        }
        self.title(titles.get(mode, "分类管理"))
        
        if mode == "delete":
            self.geometry("400x300")
        else:
            self.geometry("400x200")
        
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
        if self.mode == "delete":
            self._create_delete_widgets()
        else:
            self._create_input_widgets()
    
    def _create_input_widgets(self):
        """创建输入界面（添加/重命名）"""
        # 主容器
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 提示文本
        if self.mode == "rename":
            hint_text = f"当前分类名称: {self.category_name}"
            hint_label = ctk.CTkLabel(
                main_frame,
                text=hint_text,
                text_color=("#888888", "#888888"),
                anchor="w"
            )
            hint_label.pack(fill="x", pady=(0, 10))
        
        # 分类名称
        name_label = ctk.CTkLabel(main_frame, text="分类名称 *", anchor="w")
        name_label.pack(fill="x", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="输入分类名称")
        self.name_entry.pack(fill="x", pady=(0, 20))
        
        if self.mode == "rename" and self.category_name:
            self.name_entry.insert(0, self.category_name)
        
        # 按钮区域
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
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
        
        # 绑定回车键
        self.name_entry.bind("<Return>", lambda e: self._on_ok())
        self.bind("<Escape>", lambda e: self._on_cancel())
    
    def _create_delete_widgets(self):
        """创建删除界面"""
        # 主容器
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 提示文本
        hint_label = ctk.CTkLabel(
            main_frame,
            text="选择要删除的分类",
            font=("Microsoft YaHei UI", 12, "bold"),
            anchor="w"
        )
        hint_label.pack(fill="x", pady=(0, 10))
        
        # 分类列表
        self.category_combo = ctk.CTkComboBox(
            main_frame,
            values=self.all_categories if self.all_categories else ["无可用分类"],
            height=35,
            state="readonly"
        )
        self.category_combo.pack(fill="x", pady=(0, 10))
        
        if self.all_categories:
            self.category_combo.set(self.all_categories[0])
        
        # 警告文本
        warning_label = ctk.CTkLabel(
            main_frame,
            text="⚠️ 警告：删除分类将同时删除其中的所有启动项！",
            text_color=("#ff8800", "#ff8800"),
            wraplength=350,
            justify="center"
        )
        warning_label.pack(fill="x", pady=(10, 20))
        
        # 按钮区域
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
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
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="删除",
            width=100,
            height=35,
            fg_color=("#cc3333", "#cc3333"),
            hover_color=("#aa2222", "#aa2222"),
            command=self._on_delete
        )
        delete_btn.pack(side="right")
        
        # 绑定 ESC 键
        self.bind("<Escape>", lambda e: self._on_cancel())
    
    def _on_ok(self):
        """确定按钮"""
        name = self.name_entry.get().strip()
        
        if not name:
            self._show_error("请输入分类名称")
            return
        
        self.result = name
        self.grab_release()
        self.destroy()
    
    def _on_delete(self):
        """删除按钮"""
        if not self.all_categories:
            return
        
        selected = self.category_combo.get()
        self.result = selected
        self.grab_release()
        self.destroy()
    
    def _on_cancel(self):
        """取消按钮"""
        self.result = None
        self.grab_release()
        self.destroy()
    
    def _show_error(self, message: str):
        """显示错误提示"""
        error_label = ctk.CTkLabel(
            self,
            text=message,
            text_color=("#ff4444", "#ff4444"),
            font=("Microsoft YaHei UI", 10)
        )
        error_label.place(relx=0.5, rely=0.95, anchor="center")
        
        # 3秒后自动消失
        self.after(3000, error_label.destroy)
    
    def show(self) -> Optional[str]:
        """
        显示对话框并等待结果
        
        Returns:
            用户输入的分类名称，取消返回 None
        """
        self.wait_window()
        return self.result
