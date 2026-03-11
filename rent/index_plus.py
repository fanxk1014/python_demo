import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from paddleocr import PaddleOCR
    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False


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

    # OCR 行分组 Y 坐标阈值（像素）
    OCR_ROW_Y_THRESHOLD = 15

    # 账单字段映射规则（按优先级排序，具体关键词优先于模糊关键词）
    BILL_FIELD_MAPPING = [
        {"keyword": "电费分摊", "exclude": [], "fields": {"本期费用": "e_share"}},
        {"keyword": "电梯", "exclude": [], "fields": {"本期费用": "elevator"}},
        {"keyword": "楼梯", "exclude": [], "fields": {"本期费用": "stair"}},
        {"keyword": "水费分摊", "exclude": [], "fields": {"本期费用": "w_share"}},
        {"keyword": "电损", "exclude": [], "fields": {"单价": "e_loss_price", "本期费用": "electric_loss_total"}},
        {"keyword": "物业", "exclude": [], "fields": {"本期费用": "manage_total"}},
        {"keyword": "电费", "exclude": ["分摊", "电梯", "楼梯", "电损"],
         "fields": {"单价": "e_base_price", "本期费用": "electric_base_total"}},
        {"keyword": "水费", "exclude": ["分摊"],
         "fields": {"单价": "w_price", "本期费用": "water_total"}},
    ]

    def __init__(self, root):
        """初始化计算器界面和参数"""
        self.root = root
        self.root.title("两层楼水电费用分摊计算器（先算一楼+带计算过程）")
        self.root.geometry("900x920")

        # 初始化输入控件（便于后续取值）
        self.input_widgets = {}

        # OCR 引擎懒加载
        self._ocr_engine = None

        # 创建主界面
        self._create_main_ui()

    def _create_main_ui(self):
        """创建主界面布局（封装UI创建逻辑）"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 0. 账单图片识别区（自动填充）
        self._create_ocr_import_area(main_frame)

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

    def _create_ocr_import_area(self, parent_frame):
        """创建账单图片识别区域（OCR自动填充）"""
        frame = ttk.LabelFrame(parent_frame, text="账单图片识别（自动填充）", padding=10)
        frame.pack(fill=tk.X, pady=5)

        # 上传按钮
        btn_text = "选择账单图片..." if HAS_PADDLEOCR else "选择账单图片（未安装OCR库）"
        self._ocr_btn = ttk.Button(frame, text=btn_text, command=self._on_upload_bill_image)
        self._ocr_btn.grid(row=0, column=0, padx=(0, 10))

        if not HAS_PADDLEOCR:
            self._ocr_btn.config(state=tk.DISABLED)

        # 状态标签
        status_text = "请选择物业收费通知单图片" if HAS_PADDLEOCR else "请先安装: pip install paddlepaddle paddleocr"
        self._ocr_status_label = ttk.Label(frame, text=status_text, foreground="gray")
        self._ocr_status_label.grid(row=0, column=1, sticky=tk.W)

        # 进度条（初始隐藏）
        self._ocr_progress = ttk.Progressbar(frame, mode='indeterminate', length=300)
        self._ocr_progress.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        self._ocr_progress.grid_remove()

        # OCR 错误信息显示区（可编辑复制）
        self._ocr_error_text = tk.Text(frame, height=4, width=80, wrap=tk.WORD, 
                                        font=('Consolas', 9), fg='red')
        self._ocr_error_text.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        self._ocr_error_text.insert(tk.END, "")
        self._ocr_error_text.config(state=tk.DISABLED)

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

    # ==================== OCR 相关方法 ====================

    def _get_ocr_engine(self):
        """懒加载获取 PaddleOCR 引擎实例"""
        if self._ocr_engine is None:
            self._ocr_engine = PaddleOCR(use_textline_orientation=True, lang='ch')
        return self._ocr_engine

    def _on_upload_bill_image(self):
        """处理账单图片上传按钮点击事件"""
        image_path = filedialog.askopenfilename(
            title="选择物业收费通知单图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if not image_path:
            return

        # 禁用按钮，显示进度条
        self._ocr_btn.config(state=tk.DISABLED)
        self._ocr_status_label.config(text="正在识别，请稍候（首次使用需加载模型）...", foreground="blue")
        self._ocr_progress.grid()
        self._ocr_progress.start(10)

        # 后台线程执行 OCR
        thread = threading.Thread(target=self._run_ocr_in_background, args=(image_path,), daemon=True)
        thread.start()

    def _run_ocr_in_background(self, image_path):
        """在后台线程中执行 OCR 识别和解析"""
        try:
            engine = self._get_ocr_engine()
            # 使用 predict 方法替代已弃用的 ocr 方法
            result = engine.predict(image_path)
            if not result or not result[0]:
                self.root.after(0, self._on_ocr_complete, {}, "未识别到任何文本，请检查图片是否清晰")
                return
            parsed = self._parse_ocr_result(result[0])
            self.root.after(0, self._on_ocr_complete, parsed, None)
        except Exception as e:
            self.root.after(0, self._on_ocr_complete, {}, str(e))

    def _parse_ocr_result(self, ocr_result):
        """解析 OCR 结果，返回字段->值的映射字典"""
        rows = self._group_text_by_rows(ocr_result)
        col_positions = self._detect_header_columns(rows)
        return self._extract_field_values(rows, col_positions)

    def _group_text_by_rows(self, ocr_result):
        """按 Y 坐标将 OCR 文本块分组为行"""
        blocks = []
        for item in ocr_result:
            box, (text, confidence) = item
            # 计算中心点坐标
            x_center = (box[0][0] + box[2][0]) / 2
            y_center = (box[0][1] + box[2][1]) / 2
            blocks.append({
                "text": text.strip(),
                "confidence": confidence,
                "x_center": x_center,
                "y_center": y_center,
            })

        # 按 Y 坐标排序
        blocks.sort(key=lambda b: b["y_center"])

        # 分组：相邻 Y 差值小于阈值归入同一行
        rows = []
        current_row = []
        current_y_avg = None

        for block in blocks:
            if current_y_avg is None or abs(block["y_center"] - current_y_avg) < self.OCR_ROW_Y_THRESHOLD:
                current_row.append(block)
                current_y_avg = sum(b["y_center"] for b in current_row) / len(current_row)
            else:
                # 当前行结束，按 X 排序后存入
                current_row.sort(key=lambda b: b["x_center"])
                rows.append(current_row)
                current_row = [block]
                current_y_avg = block["y_center"]

        if current_row:
            current_row.sort(key=lambda b: b["x_center"])
            rows.append(current_row)

        return rows

    def _detect_header_columns(self, rows):
        """检测表头行，获取各列关键词的 X 坐标位置"""
        header_keywords = ["单价", "本期费用", "上期读数", "本期读数", "费用合计"]
        for row in rows:
            row_text = "".join(b["text"] for b in row)
            # 找到同时包含"单价"和"本期费用"的行即为表头
            if "单价" in row_text and "本期费用" in row_text:
                col_positions = {}
                for block in row:
                    for kw in header_keywords:
                        if kw in block["text"]:
                            col_positions[kw] = block["x_center"]
                return col_positions
        return None

    def _extract_field_values(self, rows, col_positions):
        """根据关键词匹配行，按列位置提取数值"""
        result = {}
        matched_rows = set()

        for rule in self.BILL_FIELD_MAPPING:
            keyword = rule["keyword"]
            excludes = rule["exclude"]
            fields = rule["fields"]

            for row_idx, row in enumerate(rows):
                if row_idx in matched_rows:
                    continue

                # 拼接整行文本用于匹配
                row_text = "".join(b["text"] for b in row)

                # 关键词匹配 + 排除词检查
                if keyword not in row_text:
                    continue
                if any(ex in row_text for ex in excludes):
                    continue

                # 提取行内所有数字块
                number_blocks = []
                for block in row:
                    num = self._clean_ocr_number(block["text"])
                    if num is not None:
                        number_blocks.append({"value": num, "x_center": block["x_center"]})

                if not number_blocks:
                    continue

                # 按列位置提取对应字段的值
                for col_name, field_key in fields.items():
                    value = self._find_value_by_column(number_blocks, col_positions, col_name)
                    if value is not None:
                        result[field_key] = value

                matched_rows.add(row_idx)
                break  # 每个规则只匹配一行

        return result

    def _find_value_by_column(self, number_blocks, col_positions, col_name):
        """根据列名在数字块中找到最接近对应列 X 坐标的值"""
        if col_positions and col_name in col_positions:
            target_x = col_positions[col_name]
            # 找 X 坐标最接近目标列的数字
            best = min(number_blocks, key=lambda b: abs(b["x_center"] - target_x))
            return best["value"]

        # fallback：无表头信息时，按列序号猜测
        if col_name == "本期费用" and len(number_blocks) >= 1:
            # 本期费用通常在靠右侧，取倒数第2个或倒数第3个（跳过费用合计和历史欠费）
            if len(number_blocks) >= 3:
                return number_blocks[-3]["value"]
            return number_blocks[-1]["value"]
        if col_name == "单价" and len(number_blocks) >= 4:
            # 单价在用量之后，本期费用之前
            return number_blocks[-4]["value"]
        return None

    @staticmethod
    def _clean_ocr_number(text):
        """清洗 OCR 识别的数字文本，返回浮点数或 None"""
        # 移除常见干扰字符
        cleaned = text.replace(" ", "").replace(",", "").replace("，", "")
        # 常见 OCR 误识别修正
        cleaned = cleaned.replace("O", "0").replace("o", "0")
        cleaned = cleaned.replace("l", "1").replace("I", "1")
        cleaned = cleaned.replace("~", "").replace("—", "").replace("-", "")
        # 尝试匹配数字（含小数点）
        match = re.match(r'^-?\d+\.?\d*$', cleaned)
        if match:
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _fill_input_fields(self, parsed_result):
        """将解析结果填充到输入框"""
        filled_count = 0
        for key, value in parsed_result.items():
            if key in self.input_widgets:
                widget = self.input_widgets[key]
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
                filled_count += 1
        return filled_count

    def _on_ocr_complete(self, parsed_result, error):
        """OCR 完成后的主线程回调（更新 UI 状态）"""
        # 停止并隐藏进度条
        self._ocr_progress.stop()
        self._ocr_progress.grid_remove()

        # 启用按钮
        self._ocr_btn.config(state=tk.NORMAL)
        
        # 清空错误信息区
        self._ocr_error_text.config(state=tk.NORMAL)
        self._ocr_error_text.delete(1.0, tk.END)
        
        if error:
            self._ocr_status_label.config(text=f"识别失败：{error}", foreground="red")
            # 在可编辑文本区显示详细错误信息，便于复制
            error_msg = (f"❌ OCR 识别失败\n\n"
                        f"错误详情：\n{error}\n\n"
                        f"请检查：\n"
                        f"1. 图片文件是否存在且格式正确\n"
                        f"2. 图片是否清晰可见\n"
                        f"3. 网络连接是否正常（首次使用需下载模型）")
            self._ocr_error_text.insert(tk.END, error_msg)
            self._ocr_error_text.config(state=tk.DISABLED)
            return
        
        if not parsed_result:
            self._ocr_status_label.config(text="未识别到有效费用信息，请手动填写", foreground="orange")
            self._ocr_error_text.insert(tk.END, 
                                        "⚠️ 未识别到有效的费用字段\n\n"
                                        "可能原因：\n"
                                        "1. 图片中的表格格式不标准\n"
                                        "2. 关键词匹配失败\n"
                                        "3. 需要手动调整 OCR 识别规则\n\n"
                                        "建议：请手动填写费用数据")
            self._ocr_error_text.config(state=tk.DISABLED)
            return
        
        # 填充输入框
        filled = self._fill_input_fields(parsed_result)
        self._ocr_status_label.config(
            text=f"已自动填充 {filled}/11 个字段，请检查并补充一楼读数后点击计算",
            foreground="green"
        )
        # 成功时隐藏错误信息区
        self._ocr_error_text.config(state=tk.NORMAL)
        self._ocr_error_text.delete(1.0, tk.END)
        self._ocr_error_text.config(state=tk.DISABLED)

    # ==================== 计算相关方法 ====================

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