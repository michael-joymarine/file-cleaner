#!/usr/bin/env python3
"""
Windows 定时文件清理工具 - 源码版本
与 macOS 版功能完全一致
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import schedule
from datetime import datetime
from pathlib import Path
import json

# 配置文件路径
CONFIG_FILE = Path.home() / "AppData" / "Local" / "FileCleaner" / "config.json"


class FileCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("定时文件清理工具 - Joy Marine")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # 设置窗口图标（使用默认）
        try:
            self.root.iconbitmap(default="")
        except:
            pass

        # 任务状态
        self.scheduler_thread = None
        self.stop_event = threading.Event()
        self.is_running = False
        self.next_run_time = None

        # 配置文件
        self.watch_folders = []
        self.days_threshold = 7
        self.schedule_time = "03:00"

        # 加载配置
        self.load_config()

        # 构建界面
        self.create_widgets()

        # 启动调度线程
        self.start_scheduler()

    def load_config(self):
        """加载配置文件"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.watch_folders = config.get('watch_folders', [])
                    self.days_threshold = config.get('days_threshold', 7)
                    self.schedule_time = config.get('schedule_time', "03:00")
            except Exception as e:
                print(f"加载配置失败: {e}")

    def save_config(self):
        """保存配置文件"""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'watch_folders': self.watch_folders,
                    'days_threshold': self.days_threshold,
                    'schedule_time': self.schedule_time
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def create_widgets(self):
        """构建界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="定时文件清理工具",
                                font=("Microsoft YaHei UI", 18, "bold"))
        title_label.pack(pady=(0, 10))

        subtitle_label = ttk.Label(main_frame, text="Joy Marine 专用版",
                                  font=("Microsoft YaHei UI", 10), foreground="gray")
        subtitle_label.pack(pady=(0, 20))

        # 监控文件夹区域
        folder_frame = ttk.LabelFrame(main_frame, text="监控文件夹", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 15))

        # 文件夹列表框
        list_frame = ttk.Frame(folder_frame)
        list_frame.pack(fill=tk.X)

        self.folder_listbox = tk.Listbox(list_frame, height=4, font=("Microsoft YaHei UI", 10))
        self.folder_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.folder_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.folder_listbox.config(yscrollcommand=scrollbar.set)

        # 填充现有文件夹
        for folder in self.watch_folders:
            self.folder_listbox.insert(tk.END, folder)

        # 文件夹按钮
        btn_frame = ttk.Frame(folder_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="添加文件夹", command=self.add_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="移除选中", command=self.remove_folder).pack(side=tk.LEFT)

        # 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="清理规则", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 15))

        # 文件年龄设置
        age_frame = ttk.Frame(settings_frame)
        age_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(age_frame, text="删除 ").pack(side=tk.LEFT)
        self.days_var = tk.StringVar(value=str(self.days_threshold))
        days_spinbox = ttk.Spinbox(age_frame, from_=1, to=365, width=5,
                                   textvariable=self.days_var)
        days_spinbox.pack(side=tk.LEFT)
        ttk.Label(age_frame, text=" 天前的文件").pack(side=tk.LEFT)

        # 定时设置
        time_frame = ttk.Frame(settings_frame)
        time_frame.pack(fill=tk.X)

        ttk.Label(time_frame, text="每天执行时间: ").pack(side=tk.LEFT)
        self.time_var = tk.StringVar(value=self.schedule_time)
        time_entry = ttk.Entry(time_frame, width=10, textvariable=self.time_var)
        time_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(time_frame, text="(格式: HH:MM)").pack(side=tk.LEFT)

        # 状态区域
        status_frame = ttk.LabelFrame(main_frame, text="运行状态", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 状态标签
        self.status_label = ttk.Label(status_frame, text="● 已停止",
                                     foreground="red", font=("Microsoft YaHei UI", 12))
        self.status_label.pack(pady=(0, 5))

        self.next_run_label = ttk.Label(status_frame, text="下次执行: --",
                                       foreground="gray", font=("Microsoft YaHei UI", 10))
        self.next_run_label.pack()

        # 日志区域
        self.log_text = tk.Text(status_frame, height=8, font=("Microsoft YaHei UI", 9),
                                state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        log_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL,
                                   command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scroll.set)

        # 底部按钮
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)

        self.toggle_btn = ttk.Button(bottom_frame, text="启动",
                                     command=self.toggle_scheduler)
        self.toggle_btn.pack(side=tk.LEFT)

        ttk.Button(bottom_frame, text="立即执行一次", command=self.run_clean_now).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="保存设置", command=self.save_settings).pack(side=tk.LEFT)

        self.log(f"程序启动 - 监控 {len(self.watch_folders)} 个文件夹")

    def add_folder(self):
        """添加监控文件夹"""
        folder = filedialog.askdirectory(title="选择要监控的文件夹")
        if folder and folder not in self.watch_folders:
            self.watch_folders.append(folder)
            self.folder_listbox.insert(tk.END, folder)
            self.save_config()
            self.log(f"已添加监控: {folder}")

    def remove_folder(self):
        """移除选中的文件夹"""
        selection = self.folder_listbox.curselection()
        if selection:
            index = selection[0]
            folder = self.watch_folders[index]
            self.watch_folders.pop(index)
            self.folder_listbox.delete(index)
            self.save_config()
            self.log(f"已移除监控: {folder}")

    def save_settings(self):
        """保存设置"""
        try:
            self.days_threshold = int(self.days_var.get())
            self.schedule_time = self.time_var.get()
            self.save_config()

            # 如果正在运行，重启调度器
            if self.is_running:
                self.stop_scheduler()
                self.start_scheduler()

            self.log(f"设置已保存 - 删除 {self.days_threshold} 天前文件，每天 {self.schedule_time} 执行")
            messagebox.showinfo("提示", "设置已保存")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的天数")

    def log(self, message):
        """写入日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clean_old_files(self):
        """执行文件清理"""
        self.log("=" * 50)
        self.log("开始清理任务...")

        if not self.watch_folders:
            self.log("没有配置监控文件夹")
            return

        days = int(self.days_var.get())
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 3600)

        total_deleted = 0
        total_size = 0

        for folder in self.watch_folders:
            if not os.path.exists(folder):
                self.log(f"⚠ 文件夹不存在: {folder}")
                continue

            self.log(f"扫描文件夹: {folder}")

            try:
                for root, dirs, files in os.walk(folder):
                    for filename in files:
                        filepath = os.path.join(root, filename)
                        try:
                            file_mtime = os.path.getmtime(filepath)
                            if file_mtime < cutoff_time:
                                file_size = os.path.getsize(filepath)
                                os.remove(filepath)
                                total_deleted += 1
                                total_size += file_size
                                self.log(f"  ✓ 已删除: {filename}")
                        except Exception as e:
                            self.log(f"  ✗ 删除失败 {filename}: {e}")
            except Exception as e:
                self.log(f"扫描出错: {e}")

        size_mb = total_size / (1024 * 1024)
        self.log(f"清理完成 - 共删除 {total_deleted} 个文件，释放 {size_mb:.2f} MB")
        self.log("=" * 50)

    def run_clean_now(self):
        """立即执行一次清理"""
        if not self.watch_folders:
            messagebox.showwarning("警告", "请先添加要监控的文件夹")
            return

        thread = threading.Thread(target=self.clean_old_files, daemon=True)
        thread.start()

    def toggle_scheduler(self):
        """切换调度器状态"""
        if self.is_running:
            self.stop_scheduler()
        else:
            self.start_scheduler()

    def start_scheduler(self):
        """启动调度器"""
        if not self.watch_folders:
            messagebox.showwarning("警告", "请先添加要监控的文件夹")
            return

        self.is_running = True
        self.stop_event.clear()

        # 更新界面
        self.toggle_btn.config(text="停止")
        self.status_label.config(text="● 运行中", foreground="green")

        # 启动调度线程
        self.scheduler_thread = threading.Thread(target=self.scheduler_worker, daemon=True)
        self.scheduler_thread.start()

        self.log(f"调度器已启动 - 每天 {self.schedule_time} 执行清理")

    def stop_scheduler(self):
        """停止调度器"""
        self.is_running = False
        self.stop_event.set()

        # 更新界面
        self.toggle_btn.config(text="启动")
        self.status_label.config(text="● 已停止", foreground="red")
        self.next_run_label.config(text="下次执行: --")

        self.log("调度器已停止")

    def scheduler_worker(self):
        """调度器工作线程"""
        schedule_time = self.time_var.get()

        def job():
            self.clean_old_files()

        # 清除旧任务
        schedule.clear()

        # 设置每日任务
        schedule.every().day.at(schedule_time).do(job)

        self.update_next_run()

        # 主循环
        while not self.stop_event.is_set():
            schedule.run_pending()
            self.update_next_run()
            time.sleep(30)  # 每30秒检查一次

    def update_next_run(self):
        """更新下次执行时间显示"""
        if self.is_running:
            try:
                next_run = schedule.next_run()
                if next_run:
                    self.next_run_time = next_run
                    # 在主线程更新UI
                    self.root.after(0, lambda: self.next_run_label.config(
                        text=f"下次执行: {next_run.strftime('%Y-%m-%d %H:%M:%S')}"))
            except:
                pass

    def on_closing(self):
        """窗口关闭时"""
        if self.is_running:
            self.stop_scheduler()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = FileCleanerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
