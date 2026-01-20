"""启动项添加/编辑对话框"""
import customtkinter as ctk
from tkinter import filedialog
from typing import Dict, List, Optional


class ItemDialog(ctk.CTkToplevel):
    """启动项添加/编辑对话框"""
    
    def __init__(self, parent, categories: List[str], item: Optional[Dict] = None, current_category: Optional[str] = None):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            categories: 分类列表
            item: 启动项信息（编辑模式）
            current_category: 当前分类（新增模式）
        """
        super().__init__(parent)
        
        self.result = None
        self.categories = categories
        self.item = item
        self.is_edit = item is not None
        
        # 设置窗口
        self.title("编辑启动项" if self.is_edit else "添加启动项")
        self.geometry("500x400")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets(current_category)
        
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
    
    def _create_widgets(self, current_category: Optional[str]):
        """创建对话框组件"""
        # 主容器
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 名称
        name_label = ctk.CTkLabel(main_frame, text="名称 *", anchor="w")
        name_label.pack(fill="x", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="启动项名称")
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        # 图标路径
        icon_label = ctk.CTkLabel(main_frame, text="图标路径", anchor="w")
        icon_label.pack(fill="x", pady=(0, 5))
        
        icon_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        icon_frame.pack(fill="x", pady=(0, 15))
        
        self.icon_entry = ctk.CTkEntry(icon_frame, height=35, placeholder_text="icons/default.png")
        self.icon_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        icon_browse_btn = ctk.CTkButton(
            icon_frame,
            text="浏览",
            width=80,
            height=35,
            command=self._browse_icon
        )
        icon_browse_btn.pack(side="right")
        
        # 执行路径
        path_label = ctk.CTkLabel(main_frame, text="执行路径 *", anchor="w")
        path_label.pack(fill="x", pady=(0, 5))
        
        path_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        path_frame.pack(fill="x", pady=(0, 15))
        
        self.path_entry = ctk.CTkEntry(path_frame, height=35, placeholder_text="程序路径或命令")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        path_browse_btn = ctk.CTkButton(
            path_frame,
            text="浏览",
            width=80,
            height=35,
            command=self._browse_path
        )
        path_browse_btn.pack(side="right")
        
        # 工作目录
        workdir_label = ctk.CTkLabel(main_frame, text="工作目录", anchor="w")
        workdir_label.pack(fill="x", pady=(0, 5))
        
        workdir_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        workdir_frame.pack(fill="x", pady=(0, 15))
        
        self.workdir_entry = ctk.CTkEntry(workdir_frame, height=35, placeholder_text="留空使用默认目录")
        self.workdir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        workdir_browse_btn = ctk.CTkButton(
            workdir_frame,
            text="浏览",
            width=80,
            height=35,
            command=self._browse_workdir
        )
        workdir_browse_btn.pack(side="right")
        
        # 所属分类
        category_label = ctk.CTkLabel(main_frame, text="所属分类 *", anchor="w")
        category_label.pack(fill="x", pady=(0, 5))
        
        self.category_combo = ctk.CTkComboBox(
            main_frame,
            values=self.categories,
            height=35,
            state="readonly"
        )
        self.category_combo.pack(fill="x", pady=(0, 20))
        
        # 如果是编辑模式，填充数据
        if self.is_edit and self.item:
            self.name_entry.insert(0, self.item.get("name", ""))
            self.icon_entry.insert(0, self.item.get("icon", ""))
            self.path_entry.insert(0, self.item.get("path", ""))
            self.workdir_entry.insert(0, self.item.get("workdir", ""))
        
        # 设置默认分类
        if current_category and current_category in self.categories:
            self.category_combo.set(current_category)
        elif self.categories:
            self.category_combo.set(self.categories[0])
        
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
        
        # 绑定 ESC 键
        self.bind("<Escape>", lambda e: self._on_cancel())
    
    def _browse_icon(self):
        """浏览图标文件"""
        # 临时取消置顶，让文件对话框能显示在前面
        self.attributes("-topmost", False)
        filename = filedialog.askopenfilename(
            parent=self,
            title="选择图标",
            filetypes=[
                ("图像文件", "*.png *.jpg *.jpeg *.ico *.bmp"),
                ("所有文件", "*.*")
            ]
        )
        # 恢复置顶
        self.attributes("-topmost", True)
        self.focus_force()
        
        if filename:
            self.icon_entry.delete(0, "end")
            self.icon_entry.insert(0, filename)
    
    def _browse_path(self):
        """浏览程序文件"""
        # 临时取消置顶，让文件对话框能显示在前面
        self.attributes("-topmost", False)
        filename = filedialog.askopenfilename(
            parent=self,
            title="选择程序",
            filetypes=[
                ("可执行文件", "*.exe *.bat *.cmd *.py *.lnk"),
                ("所有文件", "*.*")
            ]
        )
        # 恢复置顶
        self.attributes("-topmost", True)
        self.focus_force()
        
        if filename:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, filename)
    
    def _browse_workdir(self):
        """浏览工作目录"""
        # 临时取消置顶，让文件对话框能显示在前面
        self.attributes("-topmost", False)
        dirname = filedialog.askdirectory(
            parent=self,
            title="选择工作目录"
        )
        # 恢复置顶
        self.attributes("-topmost", True)
        self.focus_force()
        
        if dirname:
            self.workdir_entry.delete(0, "end")
            self.workdir_entry.insert(0, dirname)
    
    def _on_ok(self):
        """确定按钮"""
        # 获取输入值
        name = self.name_entry.get().strip()
        icon = self.icon_entry.get().strip()
        path = self.path_entry.get().strip()
        workdir = self.workdir_entry.get().strip()
        category = self.category_combo.get()
        
        # 验证必填项
        if not name:
            self._show_error("请输入启动项名称")
            return
        
        if not path:
            self._show_error("请输入执行路径")
            return
        
        if not category:
            self._show_error("请选择所属分类")
            return
        
        # 返回结果
        self.result = {
            "name": name,
            "icon": icon if icon else "icons/default.png",
            "path": path,
            "workdir": workdir,
            "category": category
        }
        
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
    
    def show(self) -> Optional[Dict]:
        """
        显示对话框并等待结果
        
        Returns:
            用户输入的数据，取消返回 None
        """
        self.wait_window()
        return self.result
