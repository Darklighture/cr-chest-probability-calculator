import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 用黑体显示中文
matplotlib.rcParams['axes.unicode_minus'] = False    # 正常显示负号

class ChestCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("宝箱开箱概率计算器 / Chest Probability Calculator")
        
        # 设置窗口初始大小并居中
        self.setup_window()
        
        # 语言设置
        self.language = "zh"  # 默认中文
        self.texts = {
            "zh": {
                "level_settings": "等级设置",
                "chest_levels": "宝箱等级数量:",
                "start_level": "初始等级:",
                "apply_settings": "应用设置",
                "upgrade_params": "升级参数",
                "upgrade_times": "升级次数:",
                "upgrade_prob": "等级 {}→{} 概率(%):",
                "calculate": "计算概率",
                "results": "计算结果",
                "probability_chart": "概率分布图",
                "chest_prob_calc": "宝箱概率计算",
                "chest_level": "宝箱等级",
                "probability": "概率 (%)",
                "instructions": """使用说明:
1. 设置宝箱等级数量和初始等级，点击"应用设置"
2. 设置各级升级概率(百分比)和升级次数
3. 点击"计算概率"按钮查看结果
4. 结果将显示各等级宝箱的概率和百分比
5. 右侧图表直观展示概率分布

注意:
- 升级概率是当前等级升级到下一等级的概率(百分比)
- 最高等级没有升级概率（无法继续升级）
- 概率值范围为0-100
- 初始等级必须小于等于总等级数""",
                "error": "错误",
                "invalid_levels": "宝箱等级数量必须至少为2",
                "invalid_start_level": "初始等级必须在1到{}之间",
                "invalid_level_count": "请输入有效的等级数量",
                "invalid_prob": "等级 {}→{} 的概率必须在0到100%之间",
                "invalid_upgrade_times": "升级次数不能为负数",
                "calc_error": "计算错误: {}",
                "level_prob": "等级 {} 宝箱概率: {:.6f} ({:.4f}%)",
                "level_prob_sci": "等级 {} 宝箱概率: {:.2e} ({:.2e}%)",
                "total_prob": "概率总和: {:.10f}"
            },
            "en": {
                "level_settings": "Level Settings",
                "chest_levels": "Number of Chest Levels:",
                "start_level": "Starting Level:",
                "apply_settings": "Apply Settings",
                "upgrade_params": "Upgrade Parameters",
                "upgrade_times": "Upgrade Times:",
                "upgrade_prob": "Level {}→{} Probability(%):",
                "calculate": "Calculate Probability",
                "results": "Calculation Results",
                "probability_chart": "Probability Distribution",
                "chest_prob_calc": "Chest Probability Calculation",
                "chest_level": "Chest Level",
                "probability": "Probability (%)",
                "instructions": """Instructions:
1. Set the number of chest levels and starting level, click "Apply Settings"
2. Set upgrade probabilities (percentage) and upgrade times
3. Click "Calculate Probability" to view results
4. Results will show the probability and percentage for each chest level
5. The chart on the right visually displays the probability distribution

Note:
- Upgrade probability is the probability from current level to next level (percentage)
- The highest level has no upgrade probability (cannot upgrade further)
- Probability values range from 0-100
- Starting level must be between 1 and total number of levels""",
                "error": "Error",
                "invalid_levels": "Number of chest levels must be at least 2",
                "invalid_start_level": "Starting level must be between 1 and {}",
                "invalid_level_count": "Please enter a valid number of levels",
                "invalid_prob": "Level {}→{} probability must be between 0 and 100%",
                "invalid_upgrade_times": "Upgrade times cannot be negative",
                "calc_error": "Calculation error: {}",
                "level_prob": "Level {} Chest Probability: {:.6f} ({:.4f}%)",
                "level_prob_sci": "Level {} Chest Probability: {:.2e} ({:.2e}%)",
                "total_prob": "Total Probability: {:.10f}"
            }
        }
        
        # 默认参数
        self.default_levels = 5
        self.default_upgrade_chances = [50, 45, 40, 30]  # 使用百分比格式
        self.default_n = 4
        self.default_start_level = 1
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行列权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # 语言选择框架
        self.create_language_selector()
        
        # 创建界面组件
        self.create_widgets()
        
        # 初始计算
        self.calculate_probabilities()
    
    def setup_window(self):
        """设置窗口大小和位置"""
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口大小（适应不同分辨率）
        window_width = min(1000, int(screen_width * 0.8))
        window_height = min(700, int(screen_height * 0.8))
        
        # 计算窗口位置使其居中
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口几何
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置窗口最小大小
        self.root.minsize(800, 600)
    
    def create_language_selector(self):
        """创建语言选择器"""
        lang_frame = ttk.Frame(self.main_frame)
        lang_frame.grid(row=0, column=0, columnspan=2, sticky=tk.E, pady=(0, 10))
        
        ttk.Label(lang_frame, text="Language / 语言:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.lang_var = tk.StringVar(value=self.language)
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                 values=["zh", "en"], state="readonly", width=5)
        lang_combo.pack(side=tk.LEFT)
        lang_combo.bind("<<ComboboxSelected>>", self.change_language)
    
    def create_widgets(self):
        """创建所有界面组件"""
        # 等级设置框架
        self.level_frame = ttk.LabelFrame(self.main_frame, padding="10")
        self.level_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        ttk.Label(self.level_frame, text=self.texts[self.language]["chest_levels"]).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.level_count_var = tk.IntVar(value=self.default_levels)
        self.level_count_entry = ttk.Entry(self.level_frame, textvariable=self.level_count_var, width=10)
        self.level_count_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(self.level_frame, text=self.texts[self.language]["start_level"]).grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.start_level_var = tk.IntVar(value=self.default_start_level)
        self.start_level_entry = ttk.Entry(self.level_frame, textvariable=self.start_level_var, width=10)
        self.start_level_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        self.apply_btn = ttk.Button(self.level_frame, text=self.texts[self.language]["apply_settings"], 
                                   command=self.update_level_inputs)
        self.apply_btn.grid(row=0, column=4, padx=(10, 0))
        
        # 输入框架
        self.input_frame = ttk.LabelFrame(self.main_frame, padding="10")
        self.input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 升级次数输入
        ttk.Label(self.input_frame, text=self.texts[self.language]["upgrade_times"]).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.n_var = tk.IntVar(value=self.default_n)
        self.n_entry = ttk.Entry(self.input_frame, textvariable=self.n_var, width=10)
        self.n_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # 升级概率输入区域
        self.probability_vars = []
        self.probability_entries = []
        self.probability_labels = []
        
        # 初始化升级概率输入
        self.update_level_inputs()
        
        # 结果框架
        self.result_frame = ttk.LabelFrame(self.main_frame, padding="10")
        self.result_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 创建滚动文本框显示结果
        self.result_text = tk.Text(self.result_frame, height=10, width=30)
        self.scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=self.scrollbar.set)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置结果框架的网格权重
        self.result_frame.columnconfigure(0, weight=1)
        self.result_frame.rowconfigure(0, weight=1)
        
        # 图表框架
        self.chart_frame = ttk.LabelFrame(self.main_frame, padding="10")
        self.chart_frame.grid(row=3, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建图表
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 初始化图表
        self.update_chart([1.0] + [0.0]*(self.default_levels-1))
        
        # 计算按钮框架
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        
        self.calc_btn = ttk.Button(self.button_frame, text=self.texts[self.language]["calculate"], 
                                  command=self.calculate_probabilities)
        self.calc_btn.grid(row=0, column=0)
        
        # 说明文本
        self.help_label = ttk.Label(self.main_frame, text=self.texts[self.language]["instructions"], 
                                   justify=tk.LEFT)
        self.help_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # 配置主框架的网格权重
        self.main_frame.rowconfigure(3, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # 更新所有文本
        self.update_texts()
    
    def change_language(self, event=None):
        """切换语言"""
        self.language = self.lang_var.get()
        self.update_texts()
        self.update_level_inputs()  # 重新生成输入框以更新标签
    
    def update_texts(self):
        """更新所有文本"""
        texts = self.texts[self.language]
        
        # 更新框架标签
        self.level_frame.configure(text=texts["level_settings"])
        self.input_frame.configure(text=texts["upgrade_params"])
        self.result_frame.configure(text=texts["results"])
        self.chart_frame.configure(text=texts["probability_chart"])
        
        # 更新按钮文本
        self.apply_btn.configure(text=texts["apply_settings"])
        self.calc_btn.configure(text=texts["calculate"])
        
        # 更新说明文本
        self.help_label.configure(text=texts["instructions"])
        
        # 更新等级设置标签
        for widget in self.level_frame.grid_slaves():
            if int(widget.grid_info()["row"]) == 0 and int(widget.grid_info()["column"]) == 0:
                widget.configure(text=texts["chest_levels"])
            if int(widget.grid_info()["row"]) == 0 and int(widget.grid_info()["column"]) == 2:
                widget.configure(text=texts["start_level"])
        
        # 更新升级次数标签
        for widget in self.input_frame.grid_slaves():
            if int(widget.grid_info()["row"]) == 0 and int(widget.grid_info()["column"]) == 0:
                widget.configure(text=texts["upgrade_times"])
    
    def update_level_inputs(self):
        """根据等级数量更新升级概率输入框"""
        try:
            level_count = self.level_count_var.get()
            start_level = self.start_level_var.get()
            
            if level_count < 2:
                messagebox.showerror(self.texts[self.language]["error"], 
                                    self.texts[self.language]["invalid_levels"])
                return
                
            if start_level < 1 or start_level > level_count:
                messagebox.showerror(self.texts[self.language]["error"], 
                                    self.texts[self.language]["invalid_start_level"].format(level_count))
                return
                
        except:
            messagebox.showerror(self.texts[self.language]["error"], 
                                self.texts[self.language]["invalid_level_count"])
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
                
            label_text = self.texts[self.language]["upgrade_prob"].format(i+1, i+2)
            label = ttk.Label(self.input_frame, text=label_text)
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
                raise ValueError(self.texts[self.language]["invalid_levels"])
            
            if start_level < 1 or start_level > level_count:
                raise ValueError(self.texts[self.language]["invalid_start_level"].format(level_count))
            
            if n < 0:
                raise ValueError(self.texts[self.language]["invalid_upgrade_times"])
            
            # 获取升级概率
            upgrade_probabilities = [0.0] * (level_count - 1)  # 初始化所有升级概率为0
            
            # 只设置从初始等级开始的升级概率
            for i, var in enumerate(self.probability_vars):
                prob_index = start_level - 1 + i
                if prob_index < level_count - 1:
                    prob_str = var.get()
                    prob = self.parse_percentage(prob_str)
                    if not 0 <= prob <= 1:
                        raise ValueError(self.texts[self.language]["invalid_prob"].format(prob_index+1, prob_index+2))
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
                    self.result_text.insert(tk.END, 
                                          self.texts[self.language]["level_prob_sci"].format(i+1, prob, percentage) + "\n")
                else:
                    self.result_text.insert(tk.END, 
                                          self.texts[self.language]["level_prob"].format(i+1, prob, percentage) + "\n")
                total_prob += prob
            
            self.result_text.insert(tk.END, "\n" + self.texts[self.language]["total_prob"].format(total_prob))
            
            # 更新图表
            self.update_chart(p)
            
        except Exception as e:
            # 显示错误信息
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, self.texts[self.language]["calc_error"].format(str(e)))
    
    def update_chart(self, probabilities):
        """更新概率分布图表"""
        self.ax.clear()
        
        level_count = len(probabilities)
        
        # 根据语言设置标签
        if self.language == "zh":
            levels = [f'{i+1}级宝箱' for i in range(level_count)]
            xlabel = "宝箱等级"
            ylabel = "概率 (%)"
            title = "宝箱概率计算"
        else:
            levels = [f'Level {i+1}' for i in range(level_count)]
            xlabel = "Chest Level"
            ylabel = "Probability (%)"
            title = "Chest Probability Calculation"
        
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
        
        self.ax.set_ylabel(ylabel)
        self.ax.set_xlabel(xlabel)
        self.ax.set_title(title)
        
        # 设置Y轴范围，留出一些空间
        self.ax.set_ylim(0, max_percentage * 1.15 if max_percentage > 0 else 1)
        
        # 如果等级太多，旋转X轴标签
        if level_count > 5:
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        
        self.fig.tight_layout()
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = ChestCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()