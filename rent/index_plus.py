# import tkinter as tk
# from tkinter import ttk, messagebox
#
#
# class WaterElectricityCalculator:
#     """
#     两层楼水电费用分摊计算器
#     核心功能：
#     1. 输入水电表读数、总费用、单价等信息
#     2. 按50%分摊物业管理费、公摊费用
#     3. 按不同单价计算基础电费和电损费
#     4. 自动拆分一、二楼的水电费用并展示
#     """
#     # 分摊比例常量（便于统一修改）
#     SHARE_RATIO = 0.5  # 50%均分
#
#     def __init__(self, root):
#         """初始化计算器界面和参数"""
#         self.root = root
#         self.root.title("两层楼水电费用分摊计算器")
#         self.root.geometry("800x780")
#
#         # 初始化输入控件（便于后续取值）
#         self.input_widgets = {}
#
#         # 创建主界面
#         self._create_main_ui()
#
#     def _create_main_ui(self):
#         """创建主界面布局（封装UI创建逻辑）"""
#         # 主框架
#         main_frame = ttk.Frame(self.root, padding=10)
#         main_frame.pack(fill=tk.BOTH, expand=True)
#
#         # 1. 水电表读数输入区
#         self._create_meter_input_area(main_frame)
#
#         # 2. 总费用与单价输入区
#         self._create_cost_price_input_area(main_frame)
#
#         # 3. 公摊费用输入区
#         self._create_share_cost_input_area(main_frame)
#
#         # 4. 计算按钮
#         calc_btn = ttk.Button(main_frame, text="计算费用", command=self.calculate_all)
#         calc_btn.pack(pady=10)
#
#         # 5. 结果展示区
#         self._create_result_display_area(main_frame)
#
#     def _create_meter_input_area(self, parent_frame):
#         """创建水电表读数输入区域"""
#         frame = ttk.LabelFrame(parent_frame, text="水电表读数", padding=10)
#         frame.pack(fill=tk.X, pady=5)
#
#         # 水表读数
#         self._create_label_entry(
#             frame, "一楼 上期水表读数:", row=0, col=0, widget_key="w1_last"
#         )
#         self._create_label_entry(
#             frame, "一楼 本期水表读数:", row=0, col=2, widget_key="w1_current", padx=10
#         )
#
#         # 电表读数
#         self._create_label_entry(
#             frame, "一楼 上期电表读数:", row=1, col=0, widget_key="e1_last"
#         )
#         self._create_label_entry(
#             frame, "一楼 本期电表读数:", row=1, col=2, widget_key="e1_current", padx=10
#         )
#
#     def _create_cost_price_input_area(self, parent_frame):
#         """创建总费用与单价输入区域"""
#         frame = ttk.LabelFrame(parent_frame, text="总费用与单价", padding=10)
#         frame.pack(fill=tk.X, pady=5)
#
#         # 总费用
#         self._create_label_entry(
#             frame, "总物业管理费:", row=0, col=0, widget_key="manage_total"
#         )
#         self._create_label_entry(
#             frame, "总基础电费:", row=0, col=2, widget_key="electric_base_total", padx=10
#         )
#         self._create_label_entry(
#             frame, "总电损费:", row=1, col=0, widget_key="electric_loss_total"
#         )
#         self._create_label_entry(
#             frame, "总水费:", row=1, col=2, widget_key="water_total", padx=10
#         )
#
#         # 单价
#         self._create_label_entry(
#             frame, "基础电费单价:", row=2, col=0, widget_key="e_base_price"
#         )
#         self._create_label_entry(
#             frame, "电损费单价:", row=2, col=2, widget_key="e_loss_price", padx=10
#         )
#         self._create_label_entry(
#             frame, "水费单价:", row=3, col=0, widget_key="w_price"
#         )
#
#     def _create_share_cost_input_area(self, parent_frame):
#         """创建公摊费用输入区域"""
#         frame = ttk.LabelFrame(
#             parent_frame, text=f"公摊费用（各{int(self.SHARE_RATIO * 100)}%分摊）", padding=10
#         )
#         frame.pack(fill=tk.X, pady=5)
#
#         self._create_label_entry(
#             frame, "电费分摊:", row=0, col=0, widget_key="e_share"
#         )
#         self._create_label_entry(
#             frame, "水费分摊:", row=0, col=2, widget_key="w_share", padx=10
#         )
#         self._create_label_entry(
#             frame, "电梯电费:", row=1, col=0, widget_key="elevator"
#         )
#         self._create_label_entry(
#             frame, "楼梯灯电费:", row=1, col=2, widget_key="stair", padx=10
#         )
#
#     def _create_result_display_area(self, parent_frame):
#         """创建结果展示区域"""
#         frame = ttk.LabelFrame(
#             parent_frame,
#             text=f"分摊结果（物业管理费/公摊费均按{int(self.SHARE_RATIO * 100)}%分摊）",
#             padding=10
#         )
#         frame.pack(fill=tk.BOTH, expand=True, pady=5)
#
#         # 一楼结果
#         self.floor1_text = tk.Text(frame, width=40, height=18)
#         self.floor1_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
#         self.floor1_text.insert(tk.END, "一楼费用明细:\n\n")
#         self.floor1_text.config(state=tk.DISABLED)
#
#         # 二楼结果
#         self.floor2_text = tk.Text(frame, width=40, height=18)
#         self.floor2_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
#         self.floor2_text.insert(tk.END, "二楼费用明细:\n\n")
#         self.floor2_text.config(state=tk.DISABLED)
#
#     def _create_label_entry(self, parent, text, row, col, widget_key, padx=0):
#         """
#         封装Label+Entry的创建逻辑（减少重复代码）
#         :param parent: 父容器
#         :param text: Label文本
#         :param row: 行号
#         :param col: 列号
#         :param widget_key: 控件标识（用于后续取值）
#         :param padx: 水平间距
#         """
#         label = ttk.Label(parent, text=text)
#         label.grid(row=row, column=col, sticky=tk.W, pady=2, padx=padx)
#
#         entry = ttk.Entry(parent)
#         entry.grid(row=row, column=col + 1, pady=2)
#
#         self.input_widgets[widget_key] = entry
#
#     def _get_input_value(self, key):
#         """
#         获取输入框的值并转换为浮点数
#         :param key: 控件标识
#         :return: 浮点数
#         """
#         try:
#             return float(self.input_widgets[key].get().strip())
#         except ValueError:
#             raise ValueError(f"「{key}」对应的输入值不是有效数字，请检查")
#
#     def _calculate_floor_usage(self):
#         """计算一楼水电用量"""
#         # 水费用量 = 本期 - 上期
#         w1_usage = self._get_input_value("w1_current") - self._get_input_value("w1_last")
#         # 电费用量 = 本期 - 上期
#         e1_usage = self._get_input_value("e1_current") - self._get_input_value("e1_last")
#         return w1_usage, e1_usage
#
#     def _calculate_fixed_share_cost(self):
#         """计算固定分摊费用（50%均分）"""
#         # 一楼固定分摊费用
#         f1_manage = self._get_input_value("manage_total") * self.SHARE_RATIO
#         f1_e_share = self._get_input_value("e_share") * self.SHARE_RATIO
#         f1_w_share = self._get_input_value("w_share") * self.SHARE_RATIO
#         f1_elevator = self._get_input_value("elevator") * self.SHARE_RATIO
#         f1_stair = self._get_input_value("stair") * self.SHARE_RATIO
#
#         # 二楼固定分摊费用（和一楼相同，50%均分）
#         f2_manage = f1_manage
#         f2_e_share = f1_e_share
#         f2_w_share = f1_w_share
#         f2_elevator = f1_elevator
#         f2_stair = f1_stair
#
#         return (f1_manage, f1_e_share, f1_w_share, f1_elevator, f1_stair), \
#             (f2_manage, f2_e_share, f2_w_share, f2_elevator, f2_stair)
#
#     def _calculate_usage_based_cost(self, w1_usage, e1_usage):
#         """计算按用量的费用"""
#         # 一楼按用量费用
#         f1_electric_base = e1_usage * self._get_input_value("e_base_price")  # 基础电费
#         f1_electric_loss = e1_usage * self._get_input_value("e_loss_price")  # 电损费
#         f1_water = w1_usage * self._get_input_value("w_price")  # 水费
#
#         # 二楼按用量费用 = 总费用 - 一楼费用
#         f2_electric_base = self._get_input_value("electric_base_total") - f1_electric_base
#         f2_electric_loss = self._get_input_value("electric_loss_total") - f1_electric_loss
#         f2_water = self._get_input_value("water_total") - f1_water
#
#         return (f1_electric_base, f1_electric_loss, f1_water), \
#             (f2_electric_base, f2_electric_loss, f2_water)
#
#     def _update_result_display(self, f1_costs, f2_costs):
#         """更新结果展示"""
#         # 解包费用数据
#         (f1_manage, f1_e_share, f1_w_share, f1_elevator, f1_stair), \
#             (f1_electric_base, f1_electric_loss, f1_water) = f1_costs
#
#         (f2_manage, f2_e_share, f2_w_share, f2_elevator, f2_stair), \
#             (f2_electric_base, f2_electric_loss, f2_water) = f2_costs
#
#         # 计算总计
#         f1_total = sum([f1_manage, f1_e_share, f1_w_share, f1_elevator, f1_stair,
#                         f1_electric_base, f1_electric_loss, f1_water])
#         f2_total = sum([f2_manage, f2_e_share, f2_w_share, f2_elevator, f2_stair,
#                         f2_electric_base, f2_electric_loss, f2_water])
#
#         # 更新一楼结果
#         self.floor1_text.config(state=tk.NORMAL)
#         self.floor1_text.delete(1.0, tk.END)
#         self.floor1_text.insert(tk.END, self._generate_cost_text("一楼",
#                                                                  f1_manage, f1_e_share, f1_w_share, f1_elevator,
#                                                                  f1_stair,
#                                                                  f1_electric_base, f1_electric_loss, f1_water,
#                                                                  f1_total))
#         self.floor1_text.config(state=tk.DISABLED)
#
#         # 更新二楼结果
#         self.floor2_text.config(state=tk.NORMAL)
#         self.floor2_text.delete(1.0, tk.END)
#         self.floor2_text.insert(tk.END, self._generate_cost_text("二楼",
#                                                                  f2_manage, f2_e_share, f2_w_share, f2_elevator,
#                                                                  f2_stair,
#                                                                  f2_electric_base, f2_electric_loss, f2_water,
#                                                                  f2_total))
#         self.floor2_text.config(state=tk.DISABLED)
#
#     def _generate_cost_text(self, floor_name, manage, e_share, w_share, elevator, stair,
#                             electric_base, electric_loss, water, total):
#         """生成费用明细文本（减少重复拼接）"""
#         return (
#             f"{floor_name}费用明细:\n\n"
#             f"【{int(self.SHARE_RATIO * 100)}%均分费用】\n"
#             f"物业管理费: {manage:.2f}\n"
#             f"电费分摊: {e_share:.2f}\n"
#             f"水费分摊: {w_share:.2f}\n"
#             f"电梯电费: {elevator:.2f}\n"
#             f"楼梯灯电费: {stair:.2f}\n\n"
#             f"【按用量计算】\n"
#             f"基础电费: {electric_base:.2f}\n"
#             f"电损费: {electric_loss:.2f}\n"
#             f"水费: {water:.2f}\n\n"
#             f"----------------\n"
#             f"合计: {total:.2f}\n"
#         )
#
#     def calculate_all(self):
#         """核心计算入口（对外暴露的唯一计算方法）"""
#         try:
#             # 1. 计算一楼水电用量
#             w1_usage, e1_usage = self._calculate_floor_usage()
#
#             # 2. 计算固定分摊费用
#             f1_fixed, f2_fixed = self._calculate_fixed_share_cost()
#
#             # 3. 计算按用量的费用
#             f1_usage_cost, f2_usage_cost = self._calculate_usage_based_cost(w1_usage, e1_usage)
#
#             # 4. 更新结果展示
#             self._update_result_display((f1_fixed, f1_usage_cost), (f2_fixed, f2_usage_cost))
#
#         except Exception as e:
#             messagebox.showerror("计算异常", f"请检查输入数据:\n{str(e)}")
#
#
# if __name__ == "__main__":
#     # 程序入口
#     root = tk.Tk()
#     app = WaterElectricityCalculator(root)
#     root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox


class WaterElectricityCalculator:
    """
    两层楼水电费用分摊计算器（先算一楼+展示计算过程）
    核心功能：
    1. 输入一楼水电表读数、总费用、单价、公摊费用等信息
    2. 按50%分摊物业管理费、公摊费用
    3. 先算一楼水电费用（用量×单价），总价-一楼费用=二楼费用
    4. 结果中展示完整计算过程，每一项费用标注公式和中间值
    """
    # 分摊比例常量（便于统一修改）
    SHARE_RATIO = 0.5  # 50%均分

    def __init__(self, root):
        """初始化计算器界面和参数"""
        self.root = root
        self.root.title("两层楼水电费用分摊计算器（先算一楼+带计算过程）")
        self.root.geometry("900x850")

        # 初始化输入控件（便于后续取值）
        self.input_widgets = {}

        # 创建主界面
        self._create_main_ui()

    def _create_main_ui(self):
        """创建主界面布局（封装UI创建逻辑）"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 一楼水电表读数输入区（核心计算依据）
        self._create_meter_input_area(main_frame)

        # 2. 总费用与单价输入区
        self._create_cost_price_input_area(main_frame)

        # 3. 公摊费用输入区
        self._create_share_cost_input_area(main_frame)

        # 4. 计算按钮
        calc_btn = ttk.Button(main_frame, text="计算费用", command=self.calculate_all)
        calc_btn.pack(pady=10)

        # 5. 结果展示区
        self._create_result_display_area(main_frame)

    def _create_meter_input_area(self, parent_frame):
        """创建一楼水电表读数输入区域（核心计算依据）"""
        frame = ttk.LabelFrame(parent_frame, text="一楼水电表读数（核心计算依据）", padding=10)
        frame.pack(fill=tk.X, pady=5)

        # 一楼水表读数
        self._create_label_entry(
            frame, "一楼 上期水表读数:", row=0, col=0, widget_key="w1_last"
        )
        self._create_label_entry(
            frame, "一楼 本期水表读数:", row=0, col=2, widget_key="w1_current", padx=10
        )

        # 一楼电表读数
        self._create_label_entry(
            frame, "一楼 上期电表读数:", row=1, col=0, widget_key="e1_last"
        )
        self._create_label_entry(
            frame, "一楼 本期电表读数:", row=1, col=2, widget_key="e1_current", padx=10
        )

    def _create_cost_price_input_area(self, parent_frame):
        """创建总费用与单价输入区域"""
        frame = ttk.LabelFrame(parent_frame, text="总费用与单价", padding=10)
        frame.pack(fill=tk.X, pady=5)

        # 总费用
        self._create_label_entry(
            frame, "总物业管理费:", row=0, col=0, widget_key="manage_total"
        )
        self._create_label_entry(
            frame, "总基础电费:", row=0, col=2, widget_key="electric_base_total", padx=10
        )
        self._create_label_entry(
            frame, "总电损费:", row=1, col=0, widget_key="electric_loss_total"
        )
        self._create_label_entry(
            frame, "总水费:", row=1, col=2, widget_key="water_total", padx=10
        )

        # 单价（标注单位，更清晰）
        self._create_label_entry(
            frame, "基础电费单价(元/度):", row=2, col=0, widget_key="e_base_price"
        )
        self._create_label_entry(
            frame, "电损费单价(元/度):", row=2, col=2, widget_key="e_loss_price", padx=10
        )
        self._create_label_entry(
            frame, "水费单价(元/吨):", row=3, col=0, widget_key="w_price"
        )

    def _create_share_cost_input_area(self, parent_frame):
        """创建公摊费用输入区域"""
        frame = ttk.LabelFrame(
            parent_frame, text=f"公摊费用（各{int(self.SHARE_RATIO * 100)}%分摊）", padding=10
        )
        frame.pack(fill=tk.X, pady=5)

        self._create_label_entry(
            frame, "电费分摊:", row=0, col=0, widget_key="e_share"
        )
        self._create_label_entry(
            frame, "水费分摊:", row=0, col=2, widget_key="w_share", padx=10
        )
        self._create_label_entry(
            frame, "电梯电费:", row=1, col=0, widget_key="elevator"
        )
        self._create_label_entry(
            frame, "楼梯灯电费:", row=1, col=2, widget_key="stair", padx=10
        )

    def _create_result_display_area(self, parent_frame):
        """创建结果展示区域（含计算过程）"""
        frame = ttk.LabelFrame(
            parent_frame,
            text=f"分摊结果（先算一楼费用，总价-一楼费用=二楼费用 | 含完整计算过程）",
            padding=10
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 一楼结果
        self.floor1_text = tk.Text(frame, width=45, height=20)
        self.floor1_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.floor1_text.insert(tk.END, "一楼费用明细（含计算过程）:\n\n")
        self.floor1_text.config(state=tk.DISABLED)

        # 二楼结果
        self.floor2_text = tk.Text(frame, width=45, height=20)
        self.floor2_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.floor2_text.insert(tk.END, "二楼费用明细（含计算过程）:\n\n")
        self.floor2_text.config(state=tk.DISABLED)

    def _create_label_entry(self, parent, text, row, col, widget_key, padx=0):
        """
        封装Label+Entry的创建逻辑（减少重复代码）
        :param parent: 父容器
        :param text: Label文本
        :param row: 行号
        :param col: 列号
        :param widget_key: 控件标识（用于后续取值）
        :param padx: 水平间距
        """
        label = ttk.Label(parent, text=text)
        label.grid(row=row, column=col, sticky=tk.W, pady=2, padx=padx)

        entry = ttk.Entry(parent)
        entry.grid(row=row, column=col + 1, pady=2)

        self.input_widgets[widget_key] = entry

    def _get_input_value(self, key):
        """
        获取输入框的值并转换为浮点数
        :param key: 控件标识
        :return: 浮点数
        """
        try:
            return float(self.input_widgets[key].get().strip())
        except ValueError:
            raise ValueError(f"「{key}」对应的输入值不是有效数字，请检查")

    def _calculate_floor1_usage(self):
        """仅计算一楼水电用量（核心），返回用量+原始读数（用于展示过程）"""
        # 一楼水表读数
        w1_last = self._get_input_value("w1_last")
        w1_current = self._get_input_value("w1_current")
        w1_usage = w1_current - w1_last  # 一楼用水量

        # 一楼电表读数
        e1_last = self._get_input_value("e1_last")
        e1_current = self._get_input_value("e1_current")
        e1_usage = e1_current - e1_last  # 一楼用电量

        return w1_usage, e1_usage, w1_last, w1_current, e1_last, e1_current

    def _calculate_fixed_share_cost(self):
        """计算固定分摊费用（50%均分），返回费用+总费用（用于展示过程）"""
        # 总费用
        manage_total = self._get_input_value("manage_total")
        e_share_total = self._get_input_value("e_share")
        w_share_total = self._get_input_value("w_share")
        elevator_total = self._get_input_value("elevator")
        stair_total = self._get_input_value("stair")

        # 一楼固定分摊费用（50%）
        f1_manage = manage_total * self.SHARE_RATIO
        f1_e_share = e_share_total * self.SHARE_RATIO
        f1_w_share = w_share_total * self.SHARE_RATIO
        f1_elevator = elevator_total * self.SHARE_RATIO
        f1_stair = stair_total * self.SHARE_RATIO

        # 二楼固定分摊费用（和一楼相同）
        f2_manage = f1_manage
        f2_e_share = f1_e_share
        f2_w_share = f1_w_share
        f2_elevator = f1_elevator
        f2_stair = f1_stair

        # 返回费用+总费用（用于展示计算过程）
        return (f1_manage, f1_e_share, f1_w_share, f1_elevator, f1_stair), \
            (f2_manage, f2_e_share, f2_w_share, f2_elevator, f2_stair), \
            (manage_total, e_share_total, w_share_total, elevator_total, stair_total)

    def _calculate_usage_based_cost(self, w1_usage, e1_usage):
        """计算按用量的费用（先算一楼，再用总价减一楼得二楼），返回费用+总费用+单价"""
        # 总费用和单价
        electric_base_total = self._get_input_value("electric_base_total")
        electric_loss_total = self._get_input_value("electric_loss_total")
        water_total = self._get_input_value("water_total")
        e_base_price = self._get_input_value("e_base_price")
        e_loss_price = self._get_input_value("e_loss_price")
        w_price = self._get_input_value("w_price")

        # 第一步：计算一楼按用量费用（用量×单价）
        f1_electric_base = e1_usage * e_base_price  # 一楼基础电费
        f1_electric_loss = e1_usage * e_loss_price  # 一楼电损费
        f1_water = w1_usage * w_price  # 一楼水费

        # 第二步：计算二楼按用量费用（总费用 - 一楼费用）
        f2_electric_base = electric_base_total - f1_electric_base
        f2_electric_loss = electric_loss_total - f1_electric_loss
        f2_water = water_total - f1_water

        # 返回费用+总费用+单价（用于展示计算过程）
        return (f1_electric_base, f1_electric_loss, f1_water), \
            (f2_electric_base, f2_electric_loss, f2_water), \
            (electric_base_total, electric_loss_total, water_total), \
            (e_base_price, e_loss_price, w_price)

    def _update_result_display(self, floor1_usage_data, fixed_cost_data, usage_cost_data):
        """更新结果展示（含完整计算过程）"""
        # 解包所有数据
        w1_usage, e1_usage, w1_last, w1_current, e1_last, e1_current = floor1_usage_data
        (f1_manage, f1_e_share, f1_w_share, f1_elevator, f1_stair), \
            (f2_manage, f2_e_share, f2_w_share, f2_elevator, f2_stair), \
            (manage_total, e_share_total, w_share_total, elevator_total, stair_total) = fixed_cost_data
        (f1_electric_base, f1_electric_loss, f1_water), \
            (f2_electric_base, f2_electric_loss, f2_water), \
            (electric_base_total, electric_loss_total, water_total), \
            (e_base_price, e_loss_price, w_price) = usage_cost_data

        # 计算总计
        f1_total = sum([f1_manage, f1_e_share, f1_w_share, f1_elevator, f1_stair,
                        f1_electric_base, f1_electric_loss, f1_water])
        f2_total = sum([f2_manage, f2_e_share, f2_w_share, f2_elevator, f2_stair,
                        f2_electric_base, f2_electric_loss, f2_water])

        # 生成带计算过程的文本
        floor1_text = self._generate_floor1_text(w1_usage, e1_usage, w1_last, w1_current, e1_last, e1_current,
                                                 f1_manage, f1_e_share, f1_w_share, f1_elevator, f1_stair,
                                                 f1_electric_base, f1_electric_loss, f1_water,
                                                 manage_total, e_share_total, w_share_total, elevator_total,
                                                 stair_total,
                                                 e_base_price, e_loss_price, w_price,
                                                 f1_total)

        floor2_text = self._generate_floor2_text(f2_manage, f2_e_share, f2_w_share, f2_elevator, f2_stair,
                                                 f2_electric_base, f2_electric_loss, f2_water,
                                                 manage_total, e_share_total, w_share_total, elevator_total,
                                                 stair_total,
                                                 electric_base_total, electric_loss_total, water_total,
                                                 f1_electric_base, f1_electric_loss, f1_water,
                                                 f2_total)

        # 更新一楼结果
        self.floor1_text.config(state=tk.NORMAL)
        self.floor1_text.delete(1.0, tk.END)
        self.floor1_text.insert(tk.END, floor1_text)
        self.floor1_text.config(state=tk.DISABLED)

        # 更新二楼结果
        self.floor2_text.config(state=tk.NORMAL)
        self.floor2_text.delete(1.0, tk.END)
        self.floor2_text.insert(tk.END, floor2_text)
        self.floor2_text.config(state=tk.DISABLED)

    def _generate_floor1_text(self, w1_usage, e1_usage, w1_last, w1_current, e1_last, e1_current,
                              f1_manage, f1_e_share, f1_w_share, f1_elevator, f1_stair,
                              f1_electric_base, f1_electric_loss, f1_water,
                              manage_total, e_share_total, w_share_total, elevator_total, stair_total,
                              e_base_price, e_loss_price, w_price, f1_total):
        """生成一楼带计算过程的文本"""
        return (
            f"一楼费用明细（含计算过程）:\n\n"
            f"【第一步：计算一楼用量】\n"
            f"一楼用水量 = 本期水表({w1_current:.2f}吨) - 上期水表({w1_last:.2f}吨) = {w1_usage:.2f}吨\n"
            f"一楼用电量 = 本期电表({e1_current:.2f}度) - 上期电表({e1_last:.2f}度) = {e1_usage:.2f}度\n\n"
            f"【第二步：50%均分费用（总费用×50%）】\n"
            f"物业管理费: {manage_total:.2f}元 × 50% = {f1_manage:.2f}元\n"
            f"电费分摊: {e_share_total:.2f}元 × 50% = {f1_e_share:.2f}元\n"
            f"水费分摊: {w_share_total:.2f}元 × 50% = {f1_w_share:.2f}元\n"
            f"电梯电费: {elevator_total:.2f}元 × 50% = {f1_elevator:.2f}元\n"
            f"楼梯灯电费: {stair_total:.2f}元 × 50% = {f1_stair:.2f}元\n\n"
            f"【第三步：按用量计算费用（用量×单价）】\n"
            f"基础电费: {e1_usage:.2f}度 × {e_base_price:.4f}元/度 = {f1_electric_base:.2f}元\n"
            f"电损费: {e1_usage:.2f}度 × {e_loss_price:.4f}元/度 = {f1_electric_loss:.2f}元\n"
            f"水费: {w1_usage:.2f}吨 × {w_price:.4f}元/吨 = {f1_water:.2f}元\n\n"
            f"【第四步：费用拆分总计】\n"
            f"均分费用合计: {sum([f1_manage, f1_e_share, f1_w_share, f1_elevator, f1_stair]):.2f}元\n"
            f"按用量费用合计: {sum([f1_electric_base, f1_electric_loss, f1_water]):.2f}元\n"
            f"----------------\n"
            f"一楼最终合计: {f1_total:.2f}元\n"
        )

    def _generate_floor2_text(self, f2_manage, f2_e_share, f2_w_share, f2_elevator, f2_stair,
                              f2_electric_base, f2_electric_loss, f2_water,
                              manage_total, e_share_total, w_share_total, elevator_total, stair_total,
                              electric_base_total, electric_loss_total, water_total,
                              f1_electric_base, f1_electric_loss, f1_water, f2_total):
        """生成二楼带计算过程的文本"""
        return (
            f"二楼费用明细（含计算过程）:\n\n"
            f"【第一步：50%均分费用（同一楼）】\n"
            f"物业管理费: {manage_total:.2f}元 × 50% = {f2_manage:.2f}元\n"
            f"电费分摊: {e_share_total:.2f}元 × 50% = {f2_e_share:.2f}元\n"
            f"水费分摊: {w_share_total:.2f}元 × 50% = {f2_w_share:.2f}元\n"
            f"电梯电费: {elevator_total:.2f}元 × 50% = {f2_elevator:.2f}元\n"
            f"楼梯灯电费: {stair_total:.2f}元 × 50% = {f2_stair:.2f}元\n\n"
            f"【第二步：按用量计算费用（总费用-一楼费用）】\n"
            f"基础电费: 总基础电费({electric_base_total:.2f}元) - 一楼基础电费({f1_electric_base:.2f}元) = {f2_electric_base:.2f}元\n"
            f"电损费: 总电损费({electric_loss_total:.2f}元) - 一楼电损费({f1_electric_loss:.2f}元) = {f2_electric_loss:.2f}元\n"
            f"水费: 总水费({water_total:.2f}元) - 一楼水费({f1_water:.2f}元) = {f2_water:.2f}元\n\n"
            f"【第三步：费用拆分总计】\n"
            f"均分费用合计: {sum([f2_manage, f2_e_share, f2_w_share, f2_elevator, f2_stair]):.2f}元\n"
            f"按用量费用合计: {sum([f2_electric_base, f2_electric_loss, f2_water]):.2f}元\n"
            f"----------------\n"
            f"二楼最终合计: {f2_total:.2f}元\n"
        )

    def calculate_all(self):
        """核心计算入口（先算一楼，再算二楼）"""
        try:
            # 1. 计算一楼水电用量（含原始读数，用于展示过程）
            floor1_usage_data = self._calculate_floor1_usage()

            # 2. 计算固定分摊费用（含总费用，用于展示过程）
            fixed_cost_data = self._calculate_fixed_share_cost()

            # 3. 计算按用量的费用（先算一楼，总价-一楼=二楼）
            w1_usage, e1_usage, _, _, _, _ = floor1_usage_data
            usage_cost_data = self._calculate_usage_based_cost(w1_usage, e1_usage)

            # 4. 更新结果展示（传入所有过程数据）
            self._update_result_display(floor1_usage_data, fixed_cost_data, usage_cost_data)

        except Exception as e:
            messagebox.showerror("计算异常", f"请检查输入数据:\n{str(e)}")


if __name__ == "__main__":
    # 程序入口
    root = tk.Tk()
    app = WaterElectricityCalculator(root)
    root.mainloop()