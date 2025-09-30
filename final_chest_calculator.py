import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
matplotlib.rcParams['axes.unicode_minus'] = False    # 正常显示负号

class ChestUpgradeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("宝箱升级概率计算器")
        self.root.geometry("900x700")
        
        # 默认参数
        self.default_levels = 5
        self.default_upgrade_chances = [50, 45, 40, 30]  # 使用百分比格式
        self.default_n = 4
        self.default_start_level = 1
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行列权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 等级设置框架
        level_frame = ttk.LabelFrame(main_frame, text="等级设置", padding="10")
        level_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        ttk.Label(level_frame, text="宝箱等级数量:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.level_count_var = tk.IntVar(value=self.default_levels)
        level_count_entry = ttk.Entry(level_frame, textvariable=self.level_count_var, width=10)
        level_count_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(level_frame, text="初始等级:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.start_level_var = tk.IntVar(value=self.default_start_level)
        start_level_entry = ttk.Entry(level_frame, textvariable=self.start_level_var, width=10)
        start_level_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        ttk.Button(level_frame, text="应用设置", command=self.update_level_inputs).grid(row=0, column=4, padx=(10, 0))
        
        # 输入框架
        self.input_frame = ttk.LabelFrame(main_frame, text="升级参数", padding="10")
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 升级次数输入
        ttk.Label(self.input_frame, text="升级次数:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.n_var = tk.IntVar(value=self.default_n)
        ttk.Entry(self.input_frame, textvariable=self.n_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # 升级概率输入区域
        self.probability_vars = []
        self.probability_entries = []
        self.probability_labels = []
        
        # 初始化升级概率输入
        self.update_level_inputs()
        
        # 结果框架
        result_frame = ttk.LabelFrame(main_frame, text="计算结果", padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 创建滚动文本框显示结果
        self.result_text = tk.Text(result_frame, height=10, width=30)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置结果框架的网格权重
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 图表框架
        chart_frame = ttk.LabelFrame(main_frame, text="概率分布图", padding="10")
        chart_frame.grid(row=2, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建图表
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 初始化图表
        self.update_chart([1.0] + [0.0]*(self.default_levels-1))
        
        # 计算按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        
        ttk.Button(button_frame, text="计算概率", command=self.calculate_probabilities).grid(row=0, column=0)
        
        # 说明文本
        help_text = """
使用说明:
1. 设置宝箱等级数量和初始等级，点击"应用设置"
2. 设置各级升级概率(百分比)和升级次数
3. 点击"计算概率"按钮查看结果
4. 结果将显示各等级宝箱的概率和百分比
5. 右侧图表直观展示概率分布

注意:
- 升级概率是当前等级升级到下一等级的概率(百分比)
- 最高等级没有升级概率（无法继续升级）
- 概率值范围为0-100
- 初始等级必须小于等于总等级数
        """
        help_label = ttk.Label(main_frame, text=help_text, justify=tk.LEFT)
        help_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # 配置主框架的网格权重
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def update_level_inputs(self):
        """根据等级数量更新升级概率输入框"""
        try:
            level_count = self.level_count_var.get()
            start_level = self.start_level_var.get()
            
            if level_count < 2:
                messagebox.showerror("错误", "宝箱等级数量必须至少为2")
                return
                
            if start_level < 1 or start_level > level_count:
                messagebox.showerror("错误", f"初始等级必须在1到{level_count}之间")
                return
                
        except:
            messagebox.showerror("错误", "请输入有效的等级数量")
            return
            
        # 清除现有的概率输入框
        for label in self.probability_labels:
            label.destroy()
            
        for entry in self.probability_entries:
            entry.destroy()
        
        self.probability_vars = []
        self.probability_entries = []
        self.probability_labels = []
        
        # 创建新的概率输入框
        row_offset = 1
        for i in range(level_count - 1):
            # 如果初始等级大于当前等级，则跳过这个升级概率
            if i + 1 < start_level:
                continue
                
            label = ttk.Label(self.input_frame, text=f"等级 {i+1}→{i+2} 概率(%):")
            label.grid(row=row_offset, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
            self.probability_labels.append(label)
            
            # 设置默认值，如果之前有值则使用之前的值，否则使用默认值
            default_value = self.default_upgrade_chances[i] if i < len(self.default_upgrade_chances) else 50
            var = tk.StringVar(value=str(default_value))
            self.probability_vars.append(var)
            
            entry = ttk.Entry(self.input_frame, textvariable=var, width=10)
            entry.grid(row=row_offset, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            self.probability_entries.append(entry)
            
            row_offset += 1
    
    def parse_percentage(self, value_str):
        """解析百分比输入，支持带%号和不带%号的输入"""
        try:
            # 去除空格
            value_str = value_str.strip()
            
            # 如果以%结尾，去掉%号
            if value_str.endswith('%'):
                value_str = value_str[:-1]
            
            # 转换为浮点数
            value = float(value_str)
            
            # 如果值大于1，假设是百分比格式，除以100
            if value > 1:
                value = value / 100.0
                
            return value
        except ValueError:
            raise ValueError(f"无法解析的概率值: {value_str}")
    
    def calculate_probabilities(self):
        """计算各等级宝箱的概率"""
        try:
            # 获取输入值
            level_count = self.level_count_var.get()
            start_level = self.start_level_var.get()
            n = self.n_var.get()
            
            # 验证输入
            if level_count < 2:
                raise ValueError("宝箱等级数量必须至少为2")
            
            if start_level < 1 or start_level > level_count:
                raise ValueError(f"初始等级必须在1到{level_count}之间")
            
            if n < 0:
                raise ValueError("升级次数不能为负数")
            
            # 获取升级概率
            upgrade_probabilities = [0.0] * (level_count - 1)  # 初始化所有升级概率为0
            
            # 只设置从初始等级开始的升级概率
            for i, var in enumerate(self.probability_vars):
                prob_index = start_level - 1 + i
                if prob_index < level_count - 1:
                    prob_str = var.get()
                    prob = self.parse_percentage(prob_str)
                    if not 0 <= prob <= 1:
                        raise ValueError(f"等级 {prob_index+1}→{prob_index+2} 的概率必须在0到100%之间")
                    upgrade_probabilities[prob_index] = prob
            
            # 计算概率 - 使用动态规划
            # p[i] 表示处于第i+1级的概率
            p = [0.0] * level_count
            p[start_level-1] = 1.0  # 初始状态：初始等级宝箱概率为1
            
            for _ in range(n):
                new_p = [0.0] * level_count
                
                # 处理每个等级
                for i in range(level_count):
                    if i < level_count - 1 and upgrade_probabilities[i] > 0:
                        # 可以升级的等级：部分保持原等级，部分升级
                        new_p[i] += p[i] * (1 - upgrade_probabilities[i])
                        new_p[i+1] += p[i] * upgrade_probabilities[i]
                    else:
                        # 最高等级或无法升级的等级：只能保持原等级
                        new_p[i] += p[i]
                
                p = new_p
            
            # 更新结果显示
            self.result_text.delete(1.0, tk.END)
            total_prob = 0
            for i, prob in enumerate(p):
                percentage = prob * 100
                # 对于非常小的概率，使用科学计数法显示
                if prob < 0.0001 and prob > 0:
                    self.result_text.insert(tk.END, f"等级 {i+1} 宝箱概率: {prob:.2e} ({percentage:.2e}%)\n")
                else:
                    self.result_text.insert(tk.END, f"等级 {i+1} 宝箱概率: {prob:.6f} ({percentage:.4f}%)\n")
                total_prob += prob
            
            self.result_text.insert(tk.END, f"\n概率总和: {total_prob:.10f}")
            
            # 更新图表
            self.update_chart(p)
            
        except Exception as e:
            # 显示错误信息
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"计算错误: {str(e)}")
            print(f"错误: {e}")
    
    def update_chart(self, probabilities):
        """更新概率分布图表"""
        self.ax.clear()
        
        level_count = len(probabilities)
        levels = [f'{i+1}级宝箱' for i in range(level_count)]
        
        # 将概率转换为百分比
        percentages = [p * 100 for p in probabilities]
        
        # 生成颜色
        colors = plt.cm.viridis(np.linspace(0, 1, level_count))
        
        bars = self.ax.bar(levels, percentages, color=colors)
        
        # 在柱子上添加数值标签
        max_percentage = max(percentages) if percentages else 1
        label_offset = max_percentage * 0.01  # 标签偏移量
        
        for i, bar in enumerate(bars):
            height = bar.get_height()
            # 即使概率很小也显示标签
            if height > 0:
                # 对于非常小的概率，使用科学计数法
                if height < 0.01:
                    label_text = f'{percentages[i]:.1e}%'
                else:
                    label_text = f'{percentages[i]:.2f}%'
                
                # 调整标签位置，确保即使概率很小也能看到
                va = 'bottom'
                y_pos = height + label_offset
                
                # 如果柱子高度很小，将标签放在柱子内部顶部
                if height < max_percentage * 0.05:
                    va = 'top'
                    y_pos = height - label_offset
                    # 确保不会显示在负值区域
                    if y_pos < 0:
                        y_pos = height + label_offset
                        va = 'bottom'
                
                self.ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                            label_text,
                            ha='center', va=va, fontsize=8)
        
        self.ax.set_ylabel('概率 (%)')
        self.ax.set_xlabel('宝箱等级')
        self.ax.set_title('宝箱概率计算')
        
        # 设置Y轴范围，留出一些空间
        self.ax.set_ylim(0, max_percentage * 1.15 if max_percentage > 0 else 1)
        
        # 如果等级太多，旋转X轴标签
        if level_count > 5:
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        
        self.fig.tight_layout()
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = ChestUpgradeCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()