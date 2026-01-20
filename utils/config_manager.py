"""配置文件管理模块"""
import json
import os
from typing import Dict, List, Optional
import shutil
from datetime import datetime


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config_data = None
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                self._validate_config()
            else:
                # 创建默认配置
                self.config_data = self._get_default_config()
                self.save_config()
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            self._backup_config()
            self.config_data = self._get_default_config()
            self.save_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.config_data = self._get_default_config()
    
    def _validate_config(self) -> None:
        """验证配置文件结构"""
        if not isinstance(self.config_data, dict):
            raise ValueError("配置文件根节点必须是对象")
        
        if "categories" not in self.config_data:
            self.config_data["categories"] = []
        
        if not isinstance(self.config_data["categories"], list):
            raise ValueError("categories 必须是数组")
        
        # 验证每个分类
        for category in self.config_data["categories"]:
            if "name" not in category:
                raise ValueError("分类必须包含 name 字段")
            if "items" not in category:
                category["items"] = []
            
            # 验证每个启动项
            for item in category["items"]:
                required_fields = ["name", "path"]
                for field in required_fields:
                    if field not in item:
                        raise ValueError(f"启动项必须包含 {field} 字段")
                
                # 添加默认值
                if "icon" not in item:
                    item["icon"] = "icons/default.png"
                if "workdir" not in item:
                    item["workdir"] = ""
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "categories": [
                {
                    "name": "系统工具",
                    "items": [
                        {
                            "name": "任务管理器",
                            "icon": "icons/default.png",
                            "path": "taskmgr.exe",
                            "workdir": ""
                        },
                        {
                            "name": "记事本",
                            "icon": "icons/default.png",
                            "path": "notepad.exe",
                            "workdir": ""
                        }
                    ]
                }
            ]
        }
    
    def _backup_config(self) -> None:
        """备份配置文件（错误恢复用）"""
        if os.path.exists(self.config_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.config_path}.backup_{timestamp}"
            try:
                shutil.copy2(self.config_path, backup_path)
                print(f"配置文件已备份到: {backup_path}")
            except Exception as e:
                print(f"备份配置文件失败: {e}")
    
    def _auto_backup(self) -> None:
        """自动备份配置文件（保存前）"""
        if not os.path.exists(self.config_path):
            return
        
        # 创建备份目录
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"config_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            shutil.copy2(self.config_path, backup_path)
            print(f"自动备份: {backup_path}")
            
            # 清理旧备份（只保留最近10个）
            self._cleanup_old_backups(backup_dir, max_backups=10)
        except Exception as e:
            print(f"自动备份失败: {e}")
    
    def _cleanup_old_backups(self, backup_dir: str, max_backups: int = 10) -> None:
        """清理旧备份文件"""
        try:
            # 获取所有备份文件
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith("config_backup_") and filename.endswith(".json"):
                    filepath = os.path.join(backup_dir, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            # 按时间排序
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除超出数量的旧备份
            for filepath, _ in backup_files[max_backups:]:
                os.remove(filepath)
                print(f"删除旧备份: {filepath}")
        except Exception as e:
            print(f"清理旧备份失败: {e}")
    
    def save_config(self) -> bool:
        """
        保存配置文件
            
        Returns:
            是否保存成功
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_categories(self) -> List[Dict]:
        """
        获取所有分类
        
        Returns:
            分类列表
        """
        return self.config_data.get("categories", [])
    
    def get_category(self, category_name: str) -> Optional[Dict]:
        """
        获取指定分类
        
        Args:
            category_name: 分类名称
            
        Returns:
            分类信息，不存在返回 None
        """
        for category in self.config_data.get("categories", []):
            if category["name"] == category_name:
                return category
        return None
    
    def add_category(self, category_name: str) -> bool:
        """
        添加新分类
        
        Args:
            category_name: 分类名称
            
        Returns:
            是否添加成功
        """
        if self.get_category(category_name):
            print(f"分类 '{category_name}' 已存在")
            return False
        
        new_category = {
            "name": category_name,
            "items": []
        }
        self.config_data["categories"].append(new_category)
        return self.save_config()
    
    def rename_category(self, old_name: str, new_name: str) -> bool:
        """
        重命名分类
        
        Args:
            old_name: 旧名称
            new_name: 新名称
            
        Returns:
            是否成功
        """
        if self.get_category(new_name):
            print(f"分类 '{new_name}' 已存在")
            return False
        
        category = self.get_category(old_name)
        if category:
            category["name"] = new_name
            return self.save_config()
        return False
    
    def delete_category(self, category_name: str) -> bool:
        """
        删除分类
        
        Args:
            category_name: 分类名称
            
        Returns:
            是否删除成功
        """
        categories = self.config_data.get("categories", [])
        for i, category in enumerate(categories):
            if category["name"] == category_name:
                categories.pop(i)
                return self.save_config()
        return False
    
    def add_item(self, category_name: str, item: Dict) -> bool:
        """
        添加启动项
        
        Args:
            category_name: 分类名称
            item: 启动项信息
            
        Returns:
            是否添加成功
        """
        category = self.get_category(category_name)
        if not category:
            print(f"分类 '{category_name}' 不存在")
            return False
        
        # 设置默认值
        if "icon" not in item:
            item["icon"] = "icons/default.png"
        if "workdir" not in item:
            item["workdir"] = ""
        
        category["items"].append(item)
        return self.save_config()
    
    def update_item(self, category_name: str, item_name: str, new_item: Dict) -> bool:
        """
        更新启动项
        
        Args:
            category_name: 分类名称
            item_name: 原启动项名称
            new_item: 新的启动项信息
            
        Returns:
            是否更新成功
        """
        category = self.get_category(category_name)
        if not category:
            return False
        
        for i, item in enumerate(category["items"]):
            if item["name"] == item_name:
                category["items"][i] = new_item
                return self.save_config()
        return False
    
    def delete_item(self, category_name: str, item_name: str) -> bool:
        """
        删除启动项
        
        Args:
            category_name: 分类名称
            item_name: 启动项名称
            
        Returns:
            是否删除成功
        """
        category = self.get_category(category_name)
        if not category:
            return False
        
        items = category["items"]
        for i, item in enumerate(items):
            if item["name"] == item_name:
                items.pop(i)
                return self.save_config()
        return False
    
    def move_item(self, from_category: str, to_category: str, item_name: str) -> bool:
        """
        移动启动项到其他分类
        
        Args:
            from_category: 源分类
            to_category: 目标分类
            item_name: 启动项名称
            
        Returns:
            是否移动成功
        """
        source = self.get_category(from_category)
        target = self.get_category(to_category)
        
        if not source or not target:
            return False
        
        # 查找并移除项
        item_to_move = None
        for i, item in enumerate(source["items"]):
            if item["name"] == item_name:
                item_to_move = source["items"].pop(i)
                break
        
        if item_to_move:
            target["items"].append(item_to_move)
            return self.save_config()
        
        return False
    
    def reload(self) -> None:
        """重新加载配置文件"""
        self._load_config()
    
    def export_config(self, export_path: str) -> bool:
        """
        导出配置文件
        
        Args:
            export_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
            print(f"配置已导出到: {export_path}")
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        导入配置文件
        
        Args:
            import_path: 导入文件路径
            
        Returns:
            是否导入成功
        """
        try:
            # 读取导入的配置
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # 验证配置格式
            if not isinstance(imported_data, dict) or "categories" not in imported_data:
                print("配置文件格式错误")
                return False
            
            # 备份当前配置
            self._backup_config()
            
            # 应用导入的配置
            self.config_data = imported_data
            self._validate_config()
            
            # 保存到配置文件
            return self.save_config()
        except json.JSONDecodeError as e:
            print(f"配置文件JSON格式错误: {e}")
            return False
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
    
    def get_backups(self) -> List[Dict]:
        """
        获取所有备份文件列表
        
        Returns:
            备份文件信息列表
        """
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        try:
            for filename in os.listdir(backup_dir):
                if filename.startswith("config_backup_") and filename.endswith(".json"):
                    filepath = os.path.join(backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    size = os.path.getsize(filepath)
                    
                    backups.append({
                        "filename": filename,
                        "filepath": filepath,
                        "timestamp": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "size": size
                    })
            
            # 按时间倒序排序
            backups.sort(key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            print(f"获取备份列表失败: {e}")
        
        return backups
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        恢复备份
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否恢复成功
        """
        return self.import_config(backup_path)
