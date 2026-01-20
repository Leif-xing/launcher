"""启动器面板主程序"""
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import sys
from typing import Dict, List

# 添加 utils 目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from utils.config_manager import ConfigManager
from utils.launcher import Launcher
from dialogs.message_dialog import show_error, show_question, show_info
from dialogs.item_dialog import ItemDialog
from dialogs.category_dialog import CategoryDialog
from dialogs.move_dialog import MoveDialog
from dialogs.backup_dialog import BackupDialog
from tkinter import filedialog


class LauncherCard(ctk.CTkFrame):
    """启动器卡片"""
    
    def __init__(self, master, item: Dict, category_name: str, on_click_callback, on_update_callback, **kwargs):
        """
        初始化启动器卡片
        
        Args:
            master: 父容器
            item: 启动项信息
            category_name: 所属分类
            on_click_callback: 点击回调函数
        """
        super().__init__(master, **kwargs)
        
        self.item = item
        self.category_name = category_name
        self.on_click_callback = on_click_callback
        self.on_update_callback = on_update_callback
        
        # 配置卡片样式
        self.configure(
            fg_color=("#2b2b2b", "#2b2b2b"),
            corner_radius=8,
            width=120,
            height=110
        )
        
        # 创建卡片内容
        self._create_widgets()
        
        # 绑定事件
        self.bind("<Button-1>", self._on_click)
        self.bind("<Button-3>", self._on_right_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _create_widgets(self):
        """创建卡片组件"""
        # 图标
        icon_path = self.item.get("icon", "icons/default.png")
        self.icon_label = ctk.CTkLabel(
            self,
            text="",
            width=48,
            height=48
        )
        self.icon_label.pack(pady=(15, 5))
        
        # 加载图标
        self._load_icon(icon_path)
        
        # 名称
        name = self.item.get("name", "未命名")
        self.name_label = ctk.CTkLabel(
            self,
            text=name,
            font=("Microsoft YaHei UI", 11, "bold"),
            text_color=("#ffffff", "#ffffff"),
            wraplength=110
        )
        self.name_label.pack(pady=(0, 10))
        
        # 绑定子组件事件
        for widget in [self.icon_label, self.name_label]:
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Button-3>", self._on_right_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
    
    def _load_icon(self, icon_path: str):
        """加载图标（优化性能）"""
        try:
            if os.path.exists(icon_path):
                # 缓存机制：避免重复加载相同图标
                if not hasattr(self.__class__, '_icon_cache'):
                    self.__class__._icon_cache = {}
                
                if icon_path in self.__class__._icon_cache:
                    photo = self.__class__._icon_cache[icon_path]
                else:
                    image = Image.open(icon_path)
                    image = image.resize((48, 48), Image.Resampling.LANCZOS)
                    photo = ctk.CTkImage(light_image=image, dark_image=image, size=(48, 48))
                    self.__class__._icon_cache[icon_path] = photo
                
                self.icon_label.configure(image=photo)
                self.icon_label.image = photo  # 保持引用
            else:
                # 使用默认图标文本
                self.icon_label.configure(text="📦", font=("Segoe UI Emoji", 32))
        except Exception as e:
            print(f"加载图标失败: {e}")
            self.icon_label.configure(text="📦", font=("Segoe UI Emoji", 32))
    
    def _on_click(self, event):
        """点击事件"""
        # 点击动画：缩小效果
        self._animate_click()
        
        if self.on_click_callback:
            # 延迟执行回调，让动画完成
            self.after(150, lambda: self.on_click_callback(self.item, self.category_name))
    
    def _animate_click(self):
        """点击动画效果"""
        original_width = 120
        original_height = 110
        
        # 缩小到 95%
        self.configure(width=int(original_width * 0.95), height=int(original_height * 0.95))
        
        # 100ms 后恢复原大小
        self.after(100, lambda: self.configure(width=original_width, height=original_height))
    
    def _on_right_click(self, event):
        """右键点击事件"""
        print(f"[DEBUG] 卡片右键点击: {self.item['name']}")
        
        # 如果已有菜单存在，先销毁
        if hasattr(self, '_active_menu') and self._active_menu and self._active_menu.winfo_exists():
            self._active_menu.destroy()
        
        # 创建右键菜单
        menu = ctk.CTkToplevel(self.winfo_toplevel())
        self._active_menu = menu
        menu.overrideredirect(True)
        menu.attributes("-topmost", True)
        
        # 设置菜单位置
        x = event.x_root
        y = event.y_root
        menu.geometry(f"+{x}+{y}")
        
        # 淡入动画
        menu.attributes("-alpha", 0.0)
        self._fade_in(menu)
        
        # 菜单项
        menu_frame = ctk.CTkFrame(menu, fg_color=("#2b2b2b", "#2b2b2b"), corner_radius=8)
        menu_frame.pack(padx=2, pady=2)
        
        # 编辑按钮
        edit_btn = ctk.CTkButton(
            menu_frame,
            text="编辑",
            width=120,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._menu_edit(menu)
        )
        edit_btn.pack(padx=5, pady=(5, 2))
        
        # 删除按钮
        delete_btn = ctk.CTkButton(
            menu_frame,
            text="删除",
            width=120,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._menu_delete(menu)
        )
        delete_btn.pack(padx=5, pady=2)
        
        # 移动到按钮
        move_btn = ctk.CTkButton(
            menu_frame,
            text="移动到...",
            width=120,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._menu_move(menu)
        )
        move_btn.pack(padx=5, pady=(2, 5))
        
        # 绑定关闭事件
        def close_menu(e=None):
            try:
                if menu.winfo_exists():
                    menu.destroy()
            except:
                pass
        
        # 绑定多种关闭方式
        menu.bind("<FocusOut>", close_menu)
        menu.bind("<Escape>", close_menu)
        menu.bind("<Button-1>", lambda e: close_menu() if e.widget == menu else None)
        
        # 绑定鼠标点击其他区域关闭
        def check_click(e):
            if not (menu.winfo_x() <= e.x_root <= menu.winfo_x() + menu.winfo_width() and
                    menu.winfo_y() <= e.y_root <= menu.winfo_y() + menu.winfo_height()):
                close_menu()
        
        self.winfo_toplevel().bind("<Button-1>", check_click, add="+")
        menu.bind("<Destroy>", lambda e: self.winfo_toplevel().unbind("<Button-1>"))
        
        menu.after(100, menu.focus_force)
        
        print(f"[DEBUG] 卡片菜单创建完成")
    
    def _fade_in(self, window, current_alpha=0.0):
        """淡入动画"""
        if current_alpha < 1.0:
            current_alpha = min(current_alpha + 0.15, 1.0)
            try:
                window.attributes("-alpha", current_alpha)
                window.after(20, lambda: self._fade_in(window, current_alpha))
            except:
                pass
    
    def _menu_edit(self, menu):
        """编辑菜单项"""
        menu.destroy()
        if self.on_update_callback:
            self.on_update_callback("edit", self.item, self.category_name)
    
    def _menu_delete(self, menu):
        """删除菜单项"""
        menu.destroy()
        if self.on_update_callback:
            self.on_update_callback("delete", self.item, self.category_name)
    
    def _menu_move(self, menu):
        """移动菜单项"""
        menu.destroy()
        if self.on_update_callback:
            self.on_update_callback("move", self.item, self.category_name)
    
    def _on_enter(self, event):
        """鼠标进入"""
        # 平滑过渡到悬停颜色
        self.configure(fg_color=("#3a3a3a", "#3a3a3a"))
        # 轻微放大效果
        self.configure(width=122, height=112)
    
    def _on_leave(self, event):
        """鼠标离开"""
        # 恢复原始颜色和尺寸
        self.configure(fg_color=("#2b2b2b", "#2b2b2b"))
        self.configure(width=120, height=110)


class CategoryFrame(ctk.CTkFrame):
    """分类框架"""
    
    def __init__(self, master, category: Dict, on_item_click, on_item_update, **kwargs):
        """
        初始化分类框架
        
        Args:
            master: 父容器
            category: 分类信息
            on_item_click: 启动项点击回调
        """
        super().__init__(master, **kwargs)
        
        self.category = category
        self.on_item_click = on_item_click
        self.on_item_update = on_item_update
        self.is_expanded = True
        
        # 配置框架样式
        self.configure(fg_color="transparent")
        
        # 绑定右键菜单到分类框架
        self.bind("<Button-3>", self._on_category_right_click)
        
        # 创建组件
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 标题栏
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # 分类名称
        self.title_label = ctk.CTkLabel(
            title_frame,
            text=self.category["name"],
            font=("Microsoft YaHei UI", 14, "bold"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w"
        )
        self.title_label.pack(side="left")
        
        # 折叠/展开按钮
        self.toggle_btn = ctk.CTkButton(
            title_frame,
            text="▼",
            width=30,
            height=30,
            font=("Arial", 12),
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            command=self._toggle_expand
        )
        self.toggle_btn.pack(side="right")
        
        # 卡片容器
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 绑定右键菜单到卡片容器
        self.cards_frame.bind("<Button-3>", self._on_category_right_click)
        
        # 显示卡片
        self._display_cards()
    
    def _display_cards(self):
        """显示启动项卡片"""
        items = self.category.get("items", [])
        
        # 清空现有卡片
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        # 创建网格布局
        row = 0
        col = 0
        max_cols = 5  # 每行最多5个卡片
        
        for item in items:
            card = LauncherCard(
                self.cards_frame,
                item,
                self.category["name"],
                self.on_item_click,
                self.on_item_update,
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 配置网格权重
        for i in range(max_cols):
            self.cards_frame.grid_columnconfigure(i, weight=1, uniform="cards")
    
    def _toggle_expand(self):
        """切换折叠/展开状态"""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.cards_frame.pack(fill="both", expand=True, padx=10, pady=5)
            self.toggle_btn.configure(text="▼")
        else:
            self.cards_frame.pack_forget()
            self.toggle_btn.configure(text="▶")
    
    def _on_category_right_click(self, event):
        """分类区域右键菜单"""
        # 将事件传递给主窗口处理
        # 获取主窗口并调用其右键菜单方法
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_on_background_right_click'):
            main_window._on_background_right_click(event)


class LauncherApp(ctk.CTk):
    """启动器主应用"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager("config.json")
        
        # 设置窗口
        self._setup_window()
        
        # 创建界面
        self._create_widgets()
        
        # 加载分类
        self._load_categories()
        
        # 启动动画
        self._startup_animation()
    
    def _setup_window(self):
        """设置窗口属性"""
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 窗口大小为屏幕的50%
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口
        self.title("快速启动器")
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 初始完全透明，稍后淡入
        self.attributes("-alpha", 0.0)
        
        # 设置最小尺寸
        self.minsize(600, 400)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主容器（带滚动）
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("#1a1a1a", "#1a1a1a")
        )
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # 绑定空白区域右键菜单
        self.main_frame.bind("<Button-3>", self._on_background_right_click)
    
    def _load_categories(self):
        """加载并显示所有分类"""
        # 清空现有内容
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # 获取分类
        categories = self.config_manager.get_categories()
        
        if not categories:
            # 显示空状态提示
            empty_label = ctk.CTkLabel(
                self.main_frame,
                text="暂无启动项\n右键添加分类和启动项",
                font=("Microsoft YaHei UI", 14),
                text_color=("#666666", "#666666")
            )
            empty_label.pack(expand=True)
            return
        
        # 创建分类框架
        for category in categories:
            category_frame = CategoryFrame(
                self.main_frame,
                category,
                self._on_item_click,
                self._on_item_update
            )
            category_frame.pack(fill="x", padx=10, pady=5)
    
    def _on_item_click(self, item: Dict, category_name: str):
        """
        启动项点击事件
        
        Args:
            item: 启动项信息
            category_name: 所属分类
        """
        path = item.get("path", "")
        workdir = item.get("workdir", "")
        
        print(f"启动: {item['name']} ({path})")
        
        # 验证路径
        is_valid, error_msg = Launcher.validate_path(path)
        if not is_valid:
            show_error(self, "启动失败", f"{item['name']}\n\n{error_msg}")
            return
        
        # 启动程序
        try:
            success = Launcher.launch(path, workdir if workdir else None)
            
            if success:
                # 启动成功，关闭启动器
                print(f"成功启动: {item['name']}")
                self.quit()
            else:
                # 启动失败，显示错误
                show_error(self, "启动失败", f"无法启动程序:\n{item['name']}")
        except Exception as e:
            # 捕获异常并显示
            show_error(self, "启动错误", f"{item['name']}\n\n错误信息:\n{str(e)}")
    
    def _on_background_right_click(self, event):
        """空白区域右键菜单"""
        print(f"[DEBUG] 空白区域右键点击")
        
        # 如果已有菜单存在，先销毁
        if hasattr(self, '_active_bg_menu') and self._active_bg_menu and self._active_bg_menu.winfo_exists():
            self._active_bg_menu.destroy()
        
        # 创建右键菜单
        menu = ctk.CTkToplevel(self)
        self._active_bg_menu = menu
        menu.overrideredirect(True)
        menu.attributes("-topmost", True)
        
        # 设置菜单位置
        x = event.x_root
        y = event.y_root
        menu.geometry(f"+{x}+{y}")
        
        # 淡入动画
        menu.attributes("-alpha", 0.0)
        self._fade_in_menu(menu)
        
        # 菜单项
        menu_frame = ctk.CTkFrame(menu, fg_color=("#2b2b2b", "#2b2b2b"), corner_radius=8)
        menu_frame.pack(padx=2, pady=2)
        
        # 添加启动项按钮
        add_item_btn = ctk.CTkButton(
            menu_frame,
            text="添加启动项",
            width=140,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._bg_menu_add_item(menu)
        )
        add_item_btn.pack(padx=5, pady=(5, 2))
        
        # 添加分类按钮
        add_category_btn = ctk.CTkButton(
            menu_frame,
            text="添加分类",
            width=140,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._bg_menu_add_category(menu)
        )
        add_category_btn.pack(padx=5, pady=2)
        
        # 编辑分类按钮
        edit_category_btn = ctk.CTkButton(
            menu_frame,
            text="编辑分类",
            width=140,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._bg_menu_edit_category(menu)
        )
        edit_category_btn.pack(padx=5, pady=2)
        
        # 分隔线
        separator1 = ctk.CTkFrame(menu_frame, height=1, fg_color=("#444444", "#444444"))
        separator1.pack(fill="x", padx=5, pady=5)
        
        # 导入配置按钮
        import_btn = ctk.CTkButton(
            menu_frame,
            text="导入配置",
            width=140,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._bg_menu_import(menu)
        )
        import_btn.pack(padx=5, pady=2)
        
        # 导出配置按钮
        export_btn = ctk.CTkButton(
            menu_frame,
            text="导出配置",
            width=140,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._bg_menu_export(menu)
        )
        export_btn.pack(padx=5, pady=2)
        
        # 备份管理按钮
        backup_btn = ctk.CTkButton(
            menu_frame,
            text="备份管理",
            width=140,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._bg_menu_backup(menu)
        )
        backup_btn.pack(padx=5, pady=2)
        
        # 分隔线
        separator2 = ctk.CTkFrame(menu_frame, height=1, fg_color=("#444444", "#444444"))
        separator2.pack(fill="x", padx=5, pady=5)
        
        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            menu_frame,
            text="刷新",
            width=140,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._bg_menu_refresh(menu)
        )
        refresh_btn.pack(padx=5, pady=(2, 5))
        
        # 绑定关闭事件
        def close_menu(e=None):
            try:
                if menu.winfo_exists():
                    menu.destroy()
            except:
                pass
        
        # 绑定多种关闭方式
        menu.bind("<FocusOut>", close_menu)
        menu.bind("<Escape>", close_menu)
        
        # 绑定鼠标点击其他区域关闭
        def check_click(e):
            if not (menu.winfo_x() <= e.x_root <= menu.winfo_x() + menu.winfo_width() and
                    menu.winfo_y() <= e.y_root <= menu.winfo_y() + menu.winfo_height()):
                close_menu()
        
        self.bind("<Button-1>", check_click, add="+")
        menu.bind("<Destroy>", lambda e: self.unbind("<Button-1>"))
        
        menu.after(100, menu.focus_force)
        
        print(f"[DEBUG] 空白区域菜单创建完成")
    
    def _fade_in_menu(self, window, current_alpha=0.0):
        """菜单淡入动画"""
        if current_alpha < 1.0:
            current_alpha = min(current_alpha + 0.15, 1.0)
            try:
                window.attributes("-alpha", current_alpha)
                window.after(20, lambda: self._fade_in_menu(window, current_alpha))
            except:
                pass
    
    def _on_item_update(self, action: str, item: Dict, category_name: str):
        """
        卡片更新回调
        
        Args:
            action: 操作类型 (edit, delete, move)
            item: 启动项信息
            category_name: 所属分类
        """
        if action == "edit":
            self._edit_item(item, category_name)
        elif action == "delete":
            self._delete_item(item, category_name)
        elif action == "move":
            self._move_item(item, category_name)
    
    def _edit_item(self, item: Dict, category_name: str):
        """编辑启动项"""
        categories = [cat["name"] for cat in self.config_manager.get_categories()]
        
        dialog = ItemDialog(self, categories, item, category_name)
        result = dialog.show()
        
        if result:
            old_name = item["name"]
            new_category = result.pop("category")
            
            # 如果分类改变了，先删除再添加到新分类
            if new_category != category_name:
                self.config_manager.delete_item(category_name, old_name)
                self.config_manager.add_item(new_category, result)
            else:
                # 同一分类，直接更新
                self.config_manager.update_item(category_name, old_name, result)
            
            # 刷新界面
            self._load_categories()
    
    def _delete_item(self, item: Dict, category_name: str):
        """删除启动项"""
        # 确认删除
        confirmed = show_question(
            self,
            "确认删除",
            f"确定要删除启动项 '{item['name']}' 吗？"
        )
        
        if confirmed:
            self.config_manager.delete_item(category_name, item["name"])
            self._load_categories()
    
    def _move_item(self, item: Dict, category_name: str):
        """移动启动项"""
        categories = [cat["name"] for cat in self.config_manager.get_categories()]
        
        # 移除当前分类
        target_categories = [cat for cat in categories if cat != category_name]
        
        if not target_categories:
            show_error(self, "无法移动", "没有其他可用的分类")
            return
        
        # 使用新的移动对话框
        dialog = MoveDialog(self, target_categories, category_name)
        target = dialog.show()
        
        if target:
            self.config_manager.move_item(category_name, target, item["name"])
            self._load_categories()
    
    def _bg_menu_add_item(self, menu):
        """添加启动项"""
        menu.destroy()
        
        categories = [cat["name"] for cat in self.config_manager.get_categories()]
        
        if not categories:
            show_error(self, "无法添加", "请先创建至少一个分类")
            return
        
        dialog = ItemDialog(self, categories)
        result = dialog.show()
        
        if result:
            category = result.pop("category")
            self.config_manager.add_item(category, result)
            self._load_categories()
    
    def _bg_menu_add_category(self, menu):
        """添加分类"""
        menu.destroy()
        
        dialog = CategoryDialog(self, mode="add")
        result = dialog.show()
        
        if result:
            if self.config_manager.add_category(result):
                self._load_categories()
            else:
                show_error(self, "添加失败", f"分类 '{result}' 已存在")
    
    def _bg_menu_edit_category(self, menu):
        """编辑分类"""
        menu.destroy()
        
        categories = [cat["name"] for cat in self.config_manager.get_categories()]
        
        if not categories:
            show_error(self, "无可用分类", "当前没有可编辑的分类")
            return
        
        # 先选择要编辑的分类
        dialog = CategoryDialog(self, mode="delete", all_categories=categories)
        dialog.title("选择分类")
        
        # 修改按钮文本
        for widget in dialog.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for btn in widget.winfo_children():
                    if isinstance(btn, ctk.CTkFrame):
                        for b in btn.winfo_children():
                            if isinstance(b, ctk.CTkButton) and b.cget("text") == "删除":
                                b.configure(text="选择", fg_color=("#4a9eff", "#4a9eff"))
        
        selected = dialog.show()
        
        if selected:
            # 显示重命名或删除选项
            self._show_category_edit_menu(selected)
    
    def _show_category_edit_menu(self, category_name: str):
        """显示分类编辑菜单"""
        # 创建菜单
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)
        menu.attributes("-topmost", True)
        
        # 居中显示
        x = self.winfo_x() + self.winfo_width() // 2 - 70
        y = self.winfo_y() + self.winfo_height() // 2 - 50
        menu.geometry(f"+{x}+{y}")
        
        menu_frame = ctk.CTkFrame(menu, fg_color=("#2b2b2b", "#2b2b2b"), corner_radius=8)
        menu_frame.pack(padx=2, pady=2)
        
        # 重命名按钮
        rename_btn = ctk.CTkButton(
            menu_frame,
            text="重命名",
            width=120,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._rename_category(menu, category_name)
        )
        rename_btn.pack(padx=5, pady=(5, 2))
        
        # 删除按钮
        delete_btn = ctk.CTkButton(
            menu_frame,
            text="删除",
            width=120,
            height=32,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            anchor="w",
            command=lambda: self._delete_category(menu, category_name)
        )
        delete_btn.pack(padx=5, pady=(2, 5))
        
        menu.bind("<FocusOut>", lambda e: menu.destroy())
        menu.focus_set()
    
    def _rename_category(self, menu, old_name: str):
        """重命名分类"""
        menu.destroy()
        
        dialog = CategoryDialog(self, mode="rename", category_name=old_name)
        result = dialog.show()
        
        if result:
            if self.config_manager.rename_category(old_name, result):
                self._load_categories()
            else:
                show_error(self, "重命名失败", f"分类 '{result}' 已存在")
    
    def _delete_category(self, menu, category_name: str):
        """删除分类"""
        menu.destroy()
        
        # 确认删除
        confirmed = show_question(
            self,
            "确认删除",
            f"确定要删除分类 '{category_name}' 及其所有启动项吗？\n\n此操作不可恢复！"
        )
        
        if confirmed:
            self.config_manager.delete_category(category_name)
            self._load_categories()
    
    def _bg_menu_import(self, menu):
        """导入配置"""
        menu.destroy()
        
        # 临时取消置顶
        self.attributes("-topmost", False)
        
        # 选择导入文件
        filename = filedialog.askopenfilename(
            parent=self,
            title="选择配置文件",
            filetypes=[
                ("JSON 配置文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        # 恢复置顶
        self.attributes("-topmost", False)
        self.focus_force()
        
        if filename:
            # 确认导入
            confirmed = show_question(
                self,
                "确认导入",
                f"确定要导入配置吗？\n\n当前配置将被替换！\n（当前配置会自动备份）"
            )
            
            if confirmed:
                success = self.config_manager.import_config(filename)
                if success:
                    self._load_categories()
                    show_info(self, "导入成功", "配置文件已成功导入")
                else:
                    show_error(self, "导入失败", "配置文件格式错误或读取失败")
    
    def _bg_menu_export(self, menu):
        """导出配置"""
        menu.destroy()
        
        # 临时取消置顶
        self.attributes("-topmost", False)
        
        # 选择导出位置
        filename = filedialog.asksaveasfilename(
            parent=self,
            title="导出配置文件",
            defaultextension=".json",
            filetypes=[
                ("JSON 配置文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        # 恢复置顶
        self.attributes("-topmost", False)
        self.focus_force()
        
        if filename:
            success = self.config_manager.export_config(filename)
            if success:
                show_info(self, "导出成功", f"配置已导出到:\n{filename}")
            else:
                show_error(self, "导出失败", "无法导出配置文件")
    
    def _bg_menu_backup(self, menu):
        """备份管理"""
        menu.destroy()
        
        # 获取备份列表
        backups = self.config_manager.get_backups()
        
        # 显示备份管理对话框
        dialog = BackupDialog(self, backups)
        backup_path = dialog.show()
        
        if backup_path:
            # 确认恢复
            confirmed = show_question(
                self,
                "确认恢复",
                "确定要恢复此备份吗？\n\n当前配置将被替换！"
            )
            
            if confirmed:
                success = self.config_manager.restore_backup(backup_path)
                if success:
                    self._load_categories()
                    show_info(self, "恢复成功", "配置已从备份恢复")
                else:
                    show_error(self, "恢复失败", "无法恢复备份")
    
    def _bg_menu_refresh(self, menu):
        """刷新配置"""
        menu.destroy()
        self.config_manager.reload()
        self._load_categories()
        print("配置已刷新")
    
    def _startup_animation(self):
        """启动淡入动画"""
        self._fade_in_window(0.0)
    
    def _fade_in_window(self, current_alpha=0.0):
        """窗口淡入动画"""
        if current_alpha < 0.95:
            current_alpha = min(current_alpha + 0.1, 0.95)
            try:
                self.attributes("-alpha", current_alpha)
                self.after(25, lambda: self._fade_in_window(current_alpha))
            except:
                pass


def main():
    """主函数"""
    app = LauncherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
