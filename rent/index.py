import tkinter as tk
from tkinter import ttk, messagebox

class WaterElectricityCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("两层楼水电费用分摊计算器")
        self.root.geometry("800x780")

        # 创建主框架
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 水电表读数输入区
        input_frame = ttk.LabelFrame(main_frame, text="水电表读数", padding=10)
        input_frame.pack(fill=tk.X, pady=5)

        # 水电表读数
        ttk.Label(input_frame, text="一楼 上期水表读数:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.w1_last = ttk.Entry(input_frame)
        self.w1_last.grid(row=0, column=1, pady=2)

        ttk.Label(input_frame, text="一楼 本期水表读数:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=10)
        self.w1_current = ttk.Entry(input_frame)
        self.w1_current.grid(row=0, column=3, pady=2)

        ttk.Label(input_frame, text="一楼 上期电表读数:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.e1_last = ttk.Entry(input_frame)
        self.e1_last.grid(row=1, column=1, pady=2)

        ttk.Label(input_frame, text="一楼 本期电表读数:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=10)
        self.e1_current = ttk.Entry(input_frame)
        self.e1_current.grid(row=1, column=3, pady=2)

        # 2. 总费用与单价输入区（拆分电费和电损费）
        total_frame = ttk.LabelFrame(main_frame, text="总费用与单价", padding=10)
        total_frame.pack(fill=tk.X, pady=5)

        ttk.Label(total_frame, text="总物业管理费:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.manage_total = ttk.Entry(total_frame)
        self.manage_total.grid(row=0, column=1, pady=2)

        ttk.Label(total_frame, text="总基础电费:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=10)
        self.electric_base_total = ttk.Entry(total_frame)
        self.electric_base_total.grid(row=0, column=3, pady=2)

        ttk.Label(total_frame, text="总电损费:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.electric_loss_total = ttk.Entry(total_frame)
        self.electric_loss_total.grid(row=1, column=1, pady=2)

        ttk.Label(total_frame, text="总水费:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=10)
        self.water_total = ttk.Entry(total_frame)
        self.water_total.grid(row=1, column=3, pady=2)

        ttk.Label(total_frame, text="基础电费单价:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.e_base_price = ttk.Entry(total_frame)
        self.e_base_price.grid(row=2, column=1, pady=2)

        ttk.Label(total_frame, text="电损费单价:").grid(row=2, column=2, sticky=tk.W, pady=2, padx=10)
        self.e_loss_price = ttk.Entry(total_frame)
        self.e_loss_price.grid(row=2, column=3, pady=2)

        ttk.Label(total_frame, text="水费单价:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.w_price = ttk.Entry(total_frame)
        self.w_price.grid(row=3, column=1, pady=2)

        # 3. 公摊费用输入区
        share_frame = ttk.LabelFrame(main_frame, text="公摊费用（各50%分摊）", padding=10)
        share_frame.pack(fill=tk.X, pady=5)

        ttk.Label(share_frame, text="电费分摊:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.e_share = ttk.Entry(share_frame)
        self.e_share.grid(row=0, column=1, pady=2)

        ttk.Label(share_frame, text="水费分摊:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=10)
        self.w_share = ttk.Entry(share_frame)
        self.w_share.grid(row=0, column=3, pady=2)

        ttk.Label(share_frame, text="电梯电费:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.elevator = ttk.Entry(share_frame)
        self.elevator.grid(row=1, column=1, pady=2)

        ttk.Label(share_frame, text="楼梯灯电费:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=10)
        self.stair = ttk.Entry(share_frame)
        self.stair.grid(row=1, column=3, pady=2)

        # 4. 计算按钮
        calc_btn = ttk.Button(main_frame, text="计算费用", command=self.calculate)
        calc_btn.pack(pady=10)

        # 5. 结果展示区
        result_frame = ttk.LabelFrame(main_frame, text="分摊结果（物业管理费/公摊费均按50%分摊）", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 一楼结果
        self.floor1_text = tk.Text(result_frame, width=40, height=18)
        self.floor1_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.floor1_text.insert(tk.END, "一楼费用明细:\n\n")
        self.floor1_text.config(state=tk.DISABLED)

        # 二楼结果
        self.floor2_text = tk.Text(result_frame, width=40, height=18)
        self.floor2_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.floor2_text.insert(tk.END, "二楼费用明细:\n\n")
        self.floor2_text.config(state=tk.DISABLED)

    def calculate(self):
        try:
            # 1. 读取输入数据
            # 水电表读数
            w1_last = float(self.w1_last.get())
            w1_current = float(self.w1_current.get())
            e1_last = float(self.e1_last.get())
            e1_current = float(self.e1_current.get())

            # 总费用
            manage_total = float(self.manage_total.get())  # 总物业管理费
            electric_base_total = float(self.electric_base_total.get())  # 总基础电费
            electric_loss_total = float(self.electric_loss_total.get())  # 总电损费
            water_total = float(self.water_total.get())

            # 单价（分开基础电费和电损费）
            e_base_price = float(self.e_base_price.get())  # 基础电费单价
            e_loss_price = float(self.e_loss_price.get())   # 电损费单价
            w_price = float(self.w_price.get())

            # 公摊费用
            e_share = float(self.e_share.get())
            w_share = float(self.w_share.get())
            elevator = float(self.elevator.get())
            stair = float(self.stair.get())

            # 2. 计算一、二楼用量
            w1_usage = w1_current - w1_last  # 一楼用水量
            e1_usage = e1_current - e1_last  # 一楼用电量

            # 3. 计算一楼费用（所有分摊项均按50%）
            # 固定分摊费用（50%均分）
            f1_manage = manage_total * 0.5  # 物业管理费50%
            f1_e_share = e_share * 0.5
            f1_w_share = w_share * 0.5
            f1_elevator = elevator * 0.5
            f1_stair = stair * 0.5

            # 按用量计算费用
            f1_electric_base = e1_usage * e_base_price  # 一楼基础电费
            f1_electric_loss = e1_usage * e_loss_price  # 一楼电损费
            f1_water = w1_usage * w_price               # 一楼水费

            # 一楼总费用
            f1_total = (f1_manage + f1_e_share + f1_w_share + f1_elevator + f1_stair +
                        f1_electric_base + f1_electric_loss + f1_water)

            # 4. 计算二楼费用
            # 固定分摊费用（50%均分）
            f2_manage = manage_total * 0.5  # 物业管理费50%
            f2_e_share = e_share * 0.5
            f2_w_share = w_share * 0.5
            f2_elevator = elevator * 0.5
            f2_stair = stair * 0.5

            # 按用量计算费用（总费用 - 一楼费用）
            f2_electric_base = electric_base_total - f1_electric_base  # 二楼基础电费
            f2_electric_loss = electric_loss_total - f1_electric_loss  # 二楼电损费
            f2_water = water_total - f1_water                          # 二楼水费

            # 二楼总费用
            f2_total = (f2_manage + f2_e_share + f2_w_share + f2_elevator + f2_stair +
                        f2_electric_base + f2_electric_loss + f2_water)

            # 5. 更新结果显示
            self.floor1_text.config(state=tk.NORMAL)
            self.floor1_text.delete(1.0, tk.END)
            self.floor1_text.insert(tk.END, f"一楼费用明细:\n\n"
                                           f"【50%均分费用】\n"
                                           f"物业管理费: {f1_manage:.2f}\n"
                                           f"电费分摊: {f1_e_share:.2f}\n"
                                           f"水费分摊: {f1_w_share:.2f}\n"
                                           f"电梯电费: {f1_elevator:.2f}\n"
                                           f"楼梯灯电费: {f1_stair:.2f}\n\n"
                                           f"【按用量计算】\n"
                                           f"基础电费: {f1_electric_base:.2f}\n"
                                           f"电损费: {f1_electric_loss:.2f}\n"
                                           f"水费: {f1_water:.2f}\n\n"
                                           f"----------------\n"
                                           f"合计: {f1_total:.2f}\n")
            self.floor1_text.config(state=tk.DISABLED)

            self.floor2_text.config(state=tk.NORMAL)
            self.floor2_text.delete(1.0, tk.END)
            self.floor2_text.insert(tk.END, f"二楼费用明细:\n\n"
                                           f"【50%均分费用】\n"
                                           f"物业管理费: {f2_manage:.2f}\n"
                                           f"电费分摊: {f2_e_share:.2f}\n"
                                           f"水费分摊: {f2_w_share:.2f}\n"
                                           f"电梯电费: {f2_elevator:.2f}\n"
                                           f"楼梯灯电费: {f2_stair:.2f}\n\n"
                                           f"【按用量计算】\n"
                                           f"基础电费: {f2_electric_base:.2f}\n"
                                           f"电损费: {f2_electric_loss:.2f}\n"
                                           f"水费: {f2_water:.2f}\n\n"
                                           f"----------------\n"
                                           f"合计: {f2_total:.2f}\n")
            self.floor2_text.config(state=tk.DISABLED)

        except ValueError as e:
            messagebox.showerror("输入错误", f"请确保所有输入都是数字:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("计算错误", f"计算过程中出现异常:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaterElectricityCalculator(root)
    root.mainloop()