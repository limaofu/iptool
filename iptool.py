#!/usr/bin/env python3
# coding=utf-8
# author: Cof-Lee
# this module uses the GPL-3.0 open source protocol
# update: 2024-08-24

import tkinter
from tkinter import messagebox
from tkinter import font
import cofnet

PAGE_IPV4 = 0
PAGE_IPV6 = 1
PAGE_PING = 2


class MainWindow:
    def __init__(self, width=800, height=480, title=''):
        self.title = title  # 主程序标题
        self.width = width  # 主程序界面宽度（单位：像素）
        self.height = height  # 主程序界面高度（单位：像素）
        self.resizable = True  # True 表示宽度和高度可由用户手动调整
        self.minsize = (480, 320)  # 主程序界面最小尺寸
        self.maxsize = (1920, 1080)  # 主程序界面最大尺寸
        self.background = "#3A3A3A"  # 主窗口背景色，RGB
        self.window_obj = None  # 在 MainWindow.show()里创建
        self.menu_bar = None  # 在 MainWindow.create_menu_bar_init()里创建
        self.frame_nav = None  # 导航栏frame
        self.frame_nav_height = 30  # 导航栏frame高度（单位：像素）
        self.frame_nav_button_width = 12  # 导航栏frame里的button宽度（单位：字符）
        self.frame_main_func = None  # 功能界面主frame
        self.frame_main_func_height = self.height - self.frame_nav_height  # 功能界面主frame高度（单位：像素）
        self.frame_main_func_ipv4_page = None  # 功能界面主frame里的ipv4窗口
        self.frame_main_func_ipv6_page = None  # 功能界面主frame里的ipv6窗口
        self.frame_main_func_ping_page = None  # 功能界面主frame里的ping窗口
        self.screen_width = 0  # 在 MainWindow.show()里赋值
        self.screen_height = 0  # 在 MainWindow.show()里赋值
        self.about_info_list = ["ipTool，开源的ip计算工具",
                                "版本:  v240824",
                                "本软件使用GPL-v3.0协议开源",
                                "作者:  李茂福（Cof-Lee）",
                                "更新时间: 2024-08-24"]
        self.padx = 2
        self.pady = 2
        self.view_width = 20
        self.text_font = None  # 全局字体
        self.font_family = ""  # 全局字体
        self.font_size = 18  # 全局字体大小
        self.widget_dict_ipv4 = {}  # ipv4界面的控制对象字典
        self.widget_dict_ipv6 = {}  # ipv6界面的控制对象字典
        self.current_netseg = "0.0.0.0"
        self.current_maskint = 32
        self.is_calculated = False  # 是否已计算过，ipv4
        self.is_calculated6 = False  # 是否已计算过，ipv6
        self.current_ipv6_prefix_cidrv6 = "::/128"
        self.current_ipv6_prefix_len = 128

    def show(self):
        self.window_obj = tkinter.Tk()  # ★★★创建主窗口对象★★★
        self.screen_width = self.window_obj.winfo_screenwidth()
        self.screen_height = self.window_obj.winfo_screenheight()
        self.window_obj.title(self.title)  # 设置窗口标题
        # self.window_obj.iconbitmap(bitmap="D:\\test.ico")  # 设置窗口图标，默认为羽毛图标
        win_pos_x = self.screen_width // 2 - self.width // 2
        win_pos_y = self.screen_height // 2 - self.height // 2
        win_pos = f"{self.width}x{self.height}+{win_pos_x}+{win_pos_y}"
        self.window_obj.geometry(win_pos)  # 设置窗口大小及位置，居中
        self.window_obj.resizable(width=self.resizable, height=self.resizable)  # True 表示宽度和高度可由用户手动调整
        self.window_obj.minsize(*self.minsize)  # 可调整的最小宽度及高度
        self.window_obj.maxsize(*self.maxsize)  # 可调整的最大宽度及高度
        self.window_obj.pack_propagate(True)  # True表示窗口内的控件大小自适应
        self.window_obj.configure(bg=self.background)  # 设置主窗口背景色，RGB
        # 加载初始化界面控件
        self.load_main_window_init_widget()  # ★★★ 接下来，所有的事情都在此界面操作 ★★★
        # 主窗口点击右上角的关闭按钮后，触发此函数
        self.window_obj.protocol("WM_DELETE_WINDOW", self.on_closing_main_window)
        # 运行窗口主循环
        self.window_obj.mainloop()

    def load_main_window_init_widget(self):
        """
        加载程序初始化界面控件
        :return:
        """
        # 首先清空主window
        self.clear_tkinter_widget(self.window_obj)
        # 设置全局字体
        self.text_font = font.Font(size=self.font_size, family=self.font_family)
        # 加载菜单栏
        self.create_menu_bar_init()
        # 加载导航栏
        self.create_frame_nav()
        # 添加功能窗口（默认为ipv4界面）
        self.create_frame_main_func()

    def create_frame_nav(self):
        # 创建导航栏frame
        self.frame_nav = tkinter.Frame(self.window_obj, bg="green", borderwidth=1, width=self.width, height=self.frame_nav_height,
                                       relief='groove')
        self.frame_nav.grid_propagate(False)
        self.frame_nav.pack_propagate(False)
        self.frame_nav.grid(row=0, column=0)
        # ipv4-界面按钮
        menu_button_ipv4 = tkinter.Button(self.frame_nav, text="IPv4计算", width=self.frame_nav_button_width, height=1, bg="white",
                                          command=self.frame_main_func_ipv4_page_display)
        menu_button_ipv4.pack(side=tkinter.LEFT, padx=self.padx)
        # ipv6-界面按钮
        menu_button_ipv6 = tkinter.Button(self.frame_nav, text="IPv6计算", width=self.frame_nav_button_width, height=1,
                                          bg="white",
                                          command=self.frame_main_func_ipv6_page_display)
        menu_button_ipv6.pack(side=tkinter.LEFT, padx=self.padx)
        # ping-界面按钮
        menu_button_ping = tkinter.Button(self.frame_nav, text="Ping检测", width=self.frame_nav_button_width, height=1, bg="white",
                                          command=self.frame_main_func_ping_page_display)
        menu_button_ping.pack(side=tkinter.LEFT, padx=self.padx)

    def create_frame_main_func(self):
        # 创建功能界面主frame
        self.frame_main_func = tkinter.Frame(self.window_obj, bg="pink", borderwidth=0, width=self.width,
                                             height=self.frame_main_func_height)
        self.frame_main_func.grid_propagate(False)
        self.frame_main_func.pack_propagate(False)
        self.frame_main_func.grid(row=1, column=0)
        # 创建3个功能界面子frame
        self.frame_main_func_ipv4_page = tkinter.Frame(self.frame_main_func, bg="#222222", borderwidth=0, width=self.width,
                                                       height=self.frame_main_func_height)
        self.frame_main_func_ipv6_page = tkinter.Frame(self.frame_main_func, bg="#333333", borderwidth=0, width=self.width,
                                                       height=self.frame_main_func_height)
        self.frame_main_func_ping_page = tkinter.Frame(self.frame_main_func, bg="#444444", borderwidth=0, width=self.width,
                                                       height=self.frame_main_func_height)
        # 初始化3个功能界面
        self.init_ipv4_page()
        self.init_ipv6_page()
        self.init_ping_page()
        # 首次打开程序，显示的是ipv4界面
        self.frame_main_func_ipv4_page.place(x=0, y=0, width=self.width, height=self.frame_main_func_height)
        self.widget_dict_ipv4["entry_input_ip"].focus_force()

    def frame_main_func_ipv4_page_display(self):
        # 更新导航框架 self.frame_nav 的当前选项卡背景色
        widget_index = 0
        for widget in self.frame_nav.winfo_children():
            if widget_index == PAGE_IPV4:
                widget.config(bg="pink")
            else:
                widget.config(bg="white")
            widget_index += 1
        # 显示ipv4页面
        self.frame_main_func_ipv6_page.place_forget()
        self.frame_main_func_ping_page.place_forget()
        self.frame_main_func_ipv4_page.place(x=0, y=0, width=self.width, height=self.frame_main_func_height)
        self.widget_dict_ipv4["entry_input_ip"].focus_force()

    def frame_main_func_ipv6_page_display(self):
        # 更新导航框架 self.frame_nav 的当前选项卡背景色
        widget_index = 0
        for widget in self.frame_nav.winfo_children():
            if widget_index == PAGE_IPV6:
                widget.config(bg="pink")
            else:
                widget.config(bg="white")
            widget_index += 1
        # 显示ipv4页面
        self.frame_main_func_ipv4_page.place_forget()
        self.frame_main_func_ping_page.place_forget()
        self.frame_main_func_ipv6_page.place(x=0, y=0, width=self.width, height=self.frame_main_func_height)
        self.widget_dict_ipv6["entry_input_ipv6"].focus_force()

    def frame_main_func_ping_page_display(self):
        # 更新导航框架 self.frame_nav 的当前选项卡背景色
        widget_index = 0
        for widget in self.frame_nav.winfo_children():
            if widget_index == PAGE_PING:
                widget.config(bg="pink")
            else:
                widget.config(bg="white")
            widget_index += 1
        # 显示ipv4页面
        self.frame_main_func_ipv4_page.place_forget()
        self.frame_main_func_ipv6_page.place_forget()
        self.frame_main_func_ping_page.place(x=0, y=0, width=self.width, height=self.frame_main_func_height)

    def init_ipv4_page(self):
        # 添加控件
        # 输入ip信息
        label_input_ip = tkinter.Label(self.frame_main_func_ipv4_page, text="输入ip信息★:")  # ip信息为【必填】
        label_input_ip.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.widget_dict_ipv4["sv_input_ip"] = tkinter.StringVar()
        self.widget_dict_ipv4["entry_input_ip"] = tkinter.Entry(self.frame_main_func_ipv4_page,
                                                                textvariable=self.widget_dict_ipv4["sv_input_ip"], width=48,
                                                                bg="#e2deff")
        self.widget_dict_ipv4["entry_input_ip"].grid(row=0, column=1, columnspan=2, padx=self.padx, pady=self.pady)
        self.widget_dict_ipv4["entry_input_ip"].bind("<KeyPress>", self.front_end_input_func_printable_char_ipv4)  # 监听键盘输入的字符
        # 掩码位数
        label_netmask_int = tkinter.Label(self.frame_main_func_ipv4_page, text="掩码位数:")  # 掩码位数为【选填】，在点击“计算”按钮后，会自动调到匹配值
        label_netmask_int.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.widget_dict_ipv4["sv_netmask_int"] = tkinter.StringVar()
        self.widget_dict_ipv4["spinbox_netmask_int"] = tkinter.Spinbox(self.frame_main_func_ipv4_page, from_=0, to=32, increment=1,
                                                                       textvariable=self.widget_dict_ipv4["sv_netmask_int"],
                                                                       width=3, command=self.set_netmask_scale_on_spinbox_change)
        self.widget_dict_ipv4["spinbox_netmask_int"].grid(row=1, column=1, padx=self.padx, pady=self.pady)
        self.widget_dict_ipv4["netmask_scale"] = tkinter.Scale(self.frame_main_func_ipv4_page, from_=0, to=32, resolution=1,
                                                               orient="horizontal",
                                                               showvalue=False, length=200, sliderlength=50)
        self.widget_dict_ipv4["netmask_scale"].configure(command=self.set_sv_netmask_int)
        self.widget_dict_ipv4["netmask_scale"].grid(row=1, column=2, padx=self.padx, pady=self.pady)
        # 功能按钮组
        calc_btn_frame = tkinter.Frame(self.frame_main_func_ipv4_page, width=self.width - 25, height=30, bg=self.background)
        calc_btn_frame.grid(row=2, column=0, columnspan=3)
        button_calculate = tkinter.Button(calc_btn_frame, text="计算", command=self.calculate)
        button_calculate.pack(side=tkinter.LEFT, padx=self.padx)
        button_last_netseg = tkinter.Button(calc_btn_frame, text="↑上一子网", command=self.calculate_last_netseg)
        button_last_netseg.pack(side=tkinter.LEFT, padx=self.padx)
        button_next_netseg = tkinter.Button(calc_btn_frame, text="↓下一子网", command=self.calculate_next_netseg)
        button_next_netseg.pack(side=tkinter.LEFT, padx=self.padx)
        button_clear = tkinter.Button(calc_btn_frame, text="清空", command=self.clear)
        button_clear.pack(side=tkinter.LEFT, padx=self.padx)
        button_exit = tkinter.Button(calc_btn_frame, text="退出", command=self.on_closing_main_window)
        button_exit.pack(side=tkinter.LEFT, padx=self.padx)
        # ip基础信息显示文本框
        self.widget_dict_ipv4["text_ip_base_info"] = tkinter.Text(self.frame_main_func_ipv4_page, width=60, height=7,
                                                                  font=self.text_font, bg="black", fg="white")
        self.widget_dict_ipv4["text_ip_base_info"].grid(row=3, column=0, columnspan=3, padx=self.padx, pady=self.pady)
        # ip同网段信息显示文本框
        label_other_hostseg = tkinter.Label(self.frame_main_func_ipv4_page, text="本网段其他主机ip:")
        label_other_hostseg.grid(row=4, column=0, padx=self.padx, pady=self.pady)
        self.widget_dict_ipv4["scrollbar_other_hostseg"] = tkinter.Scrollbar(self.frame_main_func_ipv4_page)
        self.widget_dict_ipv4["text_other_hostseg"] = tkinter.Text(self.frame_main_func_ipv4_page, width=60, height=9,
                                                                   font=self.text_font, bg="black", fg="white",
                                                                   yscrollcommand=self.widget_dict_ipv4["scrollbar_other_hostseg"].set)
        self.widget_dict_ipv4["text_other_hostseg"].grid(row=5, column=0, columnspan=3, padx=self.padx, pady=self.pady)
        self.widget_dict_ipv4["scrollbar_other_hostseg"].config(command=self.widget_dict_ipv4["text_other_hostseg"].yview)
        self.widget_dict_ipv4["scrollbar_other_hostseg"].grid(row=5, column=3, padx=self.padx, pady=self.pady, sticky="NS")
        # 设置Text文本框的前景色tag_config
        self.widget_dict_ipv4["text_ip_base_info"].tag_config("ip_address_fg", foreground="#deef5a")
        self.widget_dict_ipv4["text_ip_base_info"].tag_config("maskint_fg", foreground="green")
        self.widget_dict_ipv4["text_ip_base_info"].tag_config("maskbyte_fg", foreground="#0d64c0")
        self.widget_dict_ipv4["text_ip_base_info"].tag_config("hostseg_fg", foreground="pink")
        self.widget_dict_ipv4["text_ip_base_info"].tag_config("hostseg_num_fg", foreground="red")
        self.widget_dict_ipv4["text_other_hostseg"].tag_config("ip_address_fg", foreground="#deef5a")

    def init_ipv6_page(self):
        # 添加控件
        # 输入ipv6信息
        label_input_ip = tkinter.Label(self.frame_main_func_ipv6_page, text="输入ipv6信息★:")  # ip信息为【必填】
        label_input_ip.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        self.widget_dict_ipv6["sv_input_ipv6"] = tkinter.StringVar()
        self.widget_dict_ipv6["entry_input_ipv6"] = tkinter.Entry(self.frame_main_func_ipv6_page,
                                                                  textvariable=self.widget_dict_ipv6["sv_input_ipv6"], width=48,
                                                                  bg="#e2deff")
        self.widget_dict_ipv6["entry_input_ipv6"].grid(row=0, column=1, columnspan=2, padx=self.padx, pady=self.pady)
        self.widget_dict_ipv6["entry_input_ipv6"].bind("<KeyPress>", self.front_end_input_func_printable_char_ipv6)  # 监听键盘输入的字符
        # 掩码位数
        label_netmask_int = tkinter.Label(self.frame_main_func_ipv6_page, text="地址前缀长度:")  # 【选填】，在点击“计算”按钮后，会自动调到匹配值
        label_netmask_int.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        self.widget_dict_ipv6["sv_ipv6_prefix_len_int"] = tkinter.StringVar()
        self.widget_dict_ipv6["spinbox_ipv6_prefix_len_int"] = tkinter.Spinbox(self.frame_main_func_ipv6_page, from_=0, to=128, increment=1,
                                                                               textvariable=self.widget_dict_ipv6["sv_ipv6_prefix_len_int"],
                                                                               width=3,
                                                                               command=self.set_netmask_scale_on_spinbox_change_ipv6)
        self.widget_dict_ipv6["spinbox_ipv6_prefix_len_int"].grid(row=1, column=1, padx=self.padx, pady=self.pady)
        self.widget_dict_ipv6["ipv6_prefix_len_scale"] = tkinter.Scale(self.frame_main_func_ipv6_page, from_=0, to=128, resolution=1,
                                                                       orient="horizontal",
                                                                       showvalue=False, length=200, sliderlength=50)
        self.widget_dict_ipv6["ipv6_prefix_len_scale"].configure(command=self.set_sv_netmask_int_ipv6)
        self.widget_dict_ipv6["ipv6_prefix_len_scale"].grid(row=1, column=2, padx=self.padx, pady=self.pady)
        # 功能按钮组
        calc_btn_frame = tkinter.Frame(self.frame_main_func_ipv6_page, width=self.width - 25, height=30, bg=self.background)
        calc_btn_frame.grid(row=2, column=0, columnspan=3)
        button_calculate = tkinter.Button(calc_btn_frame, text="计算", command=self.calculate6)
        button_calculate.pack(side=tkinter.LEFT, padx=self.padx)
        button_last_netseg = tkinter.Button(calc_btn_frame, text="↑上一地址块", command=self.calculate_last_cidrv6)
        button_last_netseg.pack(side=tkinter.LEFT, padx=self.padx)
        button_next_netseg = tkinter.Button(calc_btn_frame, text="↓下一地址块", command=self.calculate_next_cidrv6)
        button_next_netseg.pack(side=tkinter.LEFT, padx=self.padx)
        button_clear = tkinter.Button(calc_btn_frame, text="清空", command=self.clear6)
        button_clear.pack(side=tkinter.LEFT, padx=self.padx)
        button_exit = tkinter.Button(calc_btn_frame, text="退出", command=self.on_closing_main_window)
        button_exit.pack(side=tkinter.LEFT, padx=self.padx)
        # ip基础信息显示文本框
        self.widget_dict_ipv6["text_ipv6_base_info"] = tkinter.Text(self.frame_main_func_ipv6_page, width=60, height=12,
                                                                    font=self.text_font, bg="black", fg="white")
        self.widget_dict_ipv6["text_ipv6_base_info"].grid(row=3, column=0, columnspan=3, padx=self.padx, pady=self.pady)
        # 设置Text文本框的前景色tag_config
        self.widget_dict_ipv6["text_ipv6_base_info"].tag_config("ipv6_address_fg", foreground="#deef5a")
        self.widget_dict_ipv6["text_ipv6_base_info"].tag_config("maskint_fg", foreground="green")
        self.widget_dict_ipv6["text_ipv6_base_info"].tag_config("maskbyte_fg", foreground="#0d64c0")
        self.widget_dict_ipv6["text_ipv6_base_info"].tag_config("hostseg_fg", foreground="pink")
        self.widget_dict_ipv6["text_ipv6_base_info"].tag_config("hostseg_num_fg", foreground="red")

    def init_ping_page(self):
        pass

    def front_end_input_func_printable_char_ipv4(self, event):
        """
        处理普通可打印字符，控制键及组合按键
        ★★★ 按键，ascii字符，vt100控制符是3个不同的概念
        按键可以对应一个字符，也可没有相应字符，
        按下shift/ctrl等控制键后再按其他键，可能会产生换档字符（如按下shift加数字键2，产生字符@）
        vt100控制符是由ESC（十六进制为\0x1b，八进制为\033）加其他可打印字符组成，比如:
        按键↑（方向键Up）对应的vt100控制符为 ESC加字母OA，即b'\033OA'
        ★★★
        :param event:
        :return:
        """
        # print("普通字符输入如下：")
        # print(event.keysym)
        # print(event.keycode)
        # 非可打印字符没有event.char，event.char为空，只有event.keycode
        if event.keysym == "Return":
            self.calculate()

    def front_end_input_func_printable_char_ipv6(self, event):
        # print("普通字符输入如下：")
        # print(event.keysym)
        # print(event.keycode)
        # 非可打印字符没有event.char，event.char为空，只有event.keycode
        if event.keysym == "Return":
            self.calculate6()

    def set_sv_netmask_int(self, netmask_int: int):
        # print(type(netmask_int))  # <class 'str'>
        self.widget_dict_ipv4["sv_netmask_int"].set(netmask_int)
        self.calculate(maskint=str(netmask_int))

    def set_sv_netmask_int_ipv6(self, netmask_int: int):
        self.widget_dict_ipv6["sv_ipv6_prefix_len_int"].set(netmask_int)
        self.calculate6(maskint=str(netmask_int))

    def set_netmask_scale_on_spinbox_change(self):
        netmask_int_str = self.widget_dict_ipv4["sv_netmask_int"].get()
        self.widget_dict_ipv4["netmask_scale"].set(int(netmask_int_str))
        self.calculate(maskint=netmask_int_str)

    def set_netmask_scale_on_spinbox_change_ipv6(self):
        netmask_int_str = self.widget_dict_ipv6["sv_ipv6_prefix_len_int"].get()
        self.widget_dict_ipv6["ipv6_prefix_len_scale"].set(int(netmask_int_str))
        self.calculate6(maskint=netmask_int_str)

    def clear(self):
        self.widget_dict_ipv4["sv_input_ip"].set("")
        self.widget_dict_ipv4["sv_netmask_int"].set(0)
        self.widget_dict_ipv4["netmask_scale"].set(0)
        self.widget_dict_ipv4["text_ip_base_info"].delete("1.0", tkinter.END)
        self.widget_dict_ipv4["text_other_hostseg"].delete("1.0", tkinter.END)
        self.current_netseg = ""
        self.current_maskint = 32
        self.is_calculated = False

    def clear6(self):
        self.widget_dict_ipv6["sv_input_ipv6"].set("")
        self.widget_dict_ipv6["sv_ipv6_prefix_len_int"].set(0)
        self.widget_dict_ipv6["ipv6_prefix_len_scale"].set(0)
        self.widget_dict_ipv6["text_ipv6_base_info"].delete("1.0", tkinter.END)
        # self.current_netseg = ""
        # self.current_maskint = 32
        self.is_calculated6 = False

    def calculate(self, maskint=None):
        # maskint如果要赋值，需要赋str类型的值
        input_ip_str = self.widget_dict_ipv4["sv_input_ip"].get().strip()
        if input_ip_str == "":
            return
        if cofnet.is_ip_addr(input_ip_str):  # 输入信息为 纯ip，例如 "10.99.1.3"
            self.calculate_ip(input_ip_str, maskint=maskint)
            return
        if cofnet.is_ip_maskint_addr(input_ip_str):  # 输入信息为 ip/掩码位数，例如 "10.99.1.3/24"
            self.calculate_ip_maskint(input_ip_str, maskint=maskint)
            return
        if cofnet.is_ip_range(input_ip_str):  # 输入信息为 ip-range，例如 "10.99.1.33-55"
            self.calculate_ip_range(input_ip_str)
            return
        if cofnet.is_ip_range_2(input_ip_str):  # 输入信息为 ip-range，例如 "10.99.1.33-10.99.1.55"
            self.calculate_ip_range2(input_ip_str)
            return
        if cofnet.is_cidr(input_ip_str):  # 输入信息为 cidr，例如 "10.99.1.0/24"
            self.calculate_cidr(input_ip_str)
            return
        try:
            ip_addr = cofnet.int32_to_ip(int(input_ip_str, base=16))  # 输入信息为十六进制数的ip地址
            if cofnet.is_ip_addr(ip_addr):  # 输入信息转为纯ip，例如 "10.99.1.3"
                self.calculate_ip(ip_addr, maskint=maskint)
                return
        except ValueError:
            return
        print(f"您输入的ip地址信息格式不正确 {input_ip_str}")

    def calculate6(self, maskint=None):
        # maskint如果要赋值，需要赋str类型的值
        input_ipv6_str = self.widget_dict_ipv6["sv_input_ipv6"].get().strip()
        if input_ipv6_str == "":
            return
        if cofnet.is_ipv6_addr(input_ipv6_str):  # 输入信息为 ipv6地址，例如 "FD00:1234::11"
            self.calculate6_ipv6(input_ipv6_str, ipv6_prefix_len=maskint)
            return
        if cofnet.is_cidrv6(input_ipv6_str):  # 输入信息为 cidrv6，例如 "FD00::11/64"
            self.calculate6_cidrv6(input_ipv6_str, ipv6_prefix_len=maskint)
            return
        print(f"您输入的ipv6地址信息格式不正确 {input_ipv6_str}")

    def calculate_ip(self, input_ip_str: str, maskint=None):
        """
        输入信息为 纯ip，掩码位数
        输入信息为 纯ip，子网掩码位数（可选）
        maskint如果要赋值，需要赋str类型的值
        """
        if maskint is None:
            new_maskint = "32"
        else:
            if int(maskint) < 0 or int(maskint) > 32:
                messagebox.showinfo("Error", "子网掩码应该在[0-32]区间内")
                return
            else:
                new_maskint = maskint
        self.widget_dict_ipv4["text_ip_base_info"].delete("1.0", tkinter.END)
        # 开始计算
        ip_hex_address = cofnet.ip_to_hex_string(input_ip_str)
        ip_address = f"ip地址: {input_ip_str}    ip地址十六进制表示: {ip_hex_address}\n"
        ip_int = cofnet.ip_mask_to_int(input_ip_str)
        ip_int_show = f"ip地址转为整数值: {ip_int}（十进制）\n"
        ip_binary_str = cofnet.ip_mask_to_binary_space(input_ip_str)
        ip_binary_show = f"ip地址二进制表示: {ip_binary_str}\n"
        maskbyte = cofnet.maskint_to_maskbyte(int(new_maskint))
        netseg_hex_address = cofnet.ip_to_hex_string(maskbyte)
        maskbyte_show = f"子网掩码: {maskbyte}    十六进制表示: {netseg_hex_address}\n"
        ip_netseg = cofnet.get_netseg_byte(input_ip_str, new_maskint)
        ip_hostseg = cofnet.get_hostseg_int(input_ip_str, new_maskint)
        host_seg_num = cofnet.get_hostseg_num(int(new_maskint))
        ip_netseg_hex_address = cofnet.ip_to_hex_string(ip_netseg)
        ip_netseg_info = f"ip地址对应网络号: {ip_netseg}/{new_maskint}  十六进制表示: {ip_netseg_hex_address}\n"
        ip_hostseg_info = f"本ip为本网段第 {ip_hostseg + 1} 个ip（第1个ip是主机号为全0的ip）\n主机号可用ip总量: {host_seg_num}\n"
        # 将ip相关信息输出到Text控件中
        self.widget_dict_ipv4["text_ip_base_info"].insert(tkinter.END, ip_address)
        start_index1 = "1.6"
        end_index1 = "1." + str(6 + len(input_ip_str))
        self.widget_dict_ipv4["text_ip_base_info"].tag_add("ip_address_fg", start_index1, end_index1)
        self.widget_dict_ipv4["text_ip_base_info"].insert(tkinter.END, ip_int_show)
        self.widget_dict_ipv4["text_ip_base_info"].insert(tkinter.END, ip_binary_show)
        new_maskint_with_space = cofnet.get_maskint_with_space(int(new_maskint))
        start_index2 = "3.11"
        end_index2 = "3." + str(11 + new_maskint_with_space)
        self.widget_dict_ipv4["text_ip_base_info"].tag_add("maskint_fg", start_index2, end_index2)
        self.widget_dict_ipv4["text_ip_base_info"].tag_add("hostseg_fg", end_index2, end_index2 + " lineend")
        self.widget_dict_ipv4["text_ip_base_info"].insert(tkinter.END, maskbyte_show)
        start_index3 = "4.6"
        end_index3 = "4." + str(6 + len(maskbyte))
        self.widget_dict_ipv4["text_ip_base_info"].tag_add("maskbyte_fg", start_index3, end_index3)
        self.widget_dict_ipv4["text_ip_base_info"].insert(tkinter.END, ip_netseg_info)
        start_index4 = "5.11"
        end_index4 = "5." + str(11 + len(ip_netseg))
        start_index4_2 = "5." + str(12 + len(ip_netseg))
        end_index4_2 = "5." + str(12 + len(str(new_maskint)))
        self.widget_dict_ipv4["text_ip_base_info"].tag_add("maskint_fg", start_index4, end_index4)
        self.widget_dict_ipv4["text_ip_base_info"].tag_add("maskbyte_fg", start_index4_2, end_index4_2)
        self.widget_dict_ipv4["text_ip_base_info"].insert(tkinter.END, ip_hostseg_info)
        start_index5 = "6.9"
        end_index5 = "6." + str(9 + len(str(ip_hostseg)))
        self.widget_dict_ipv4["text_ip_base_info"].tag_add("hostseg_fg", start_index5, end_index5)
        self.widget_dict_ipv4["text_ip_base_info"].tag_add("hostseg_num_fg", "7.11", tkinter.END)
        # 更新子网掩码滑块及spinbox的值
        self.widget_dict_ipv4["sv_netmask_int"].set(int(new_maskint))
        self.widget_dict_ipv4["netmask_scale"].set(int(new_maskint))
        # 输出同一网段下的所有主机ip
        self.widget_dict_ipv4["text_other_hostseg"].delete("1.0", tkinter.END)
        if host_seg_num > 65536:  # 小于16位掩码时不再显示同网段所有ip
            self.widget_dict_ipv4["text_other_hostseg"].insert(tkinter.END, "抱歉，ip数量太多了，这里基于性能考量，不再显示本网段所有ip地址")
        else:
            head = "序号\tip地址\t备注\n"
            self.widget_dict_ipv4["text_other_hostseg"].insert(tkinter.END, head)
            ip_netseg_int = cofnet.get_netseg_int(input_ip_str, new_maskint)
            for i in range(host_seg_num):
                ip_address = cofnet.int32_to_ip(ip_netseg_int + i)
                if i == ip_hostseg and i == 0:
                    ip_line_info = str(i + 1) + "\t" + ip_address + "\t此ip为您输入的ip（主机号为全0）\n"
                elif i == ip_hostseg and i == host_seg_num - 1:
                    ip_line_info = str(i + 1) + "\t" + ip_address + "\t此ip为您输入的ip（主机号为全1）\n"
                elif i == ip_hostseg:
                    ip_line_info = str(i + 1) + "\t" + ip_address + "\t此ip为您输入的ip\n"
                elif i == 0:
                    ip_line_info = str(i + 1) + "\t" + ip_address + "\t此ip主机号为全0\n"
                elif i == host_seg_num - 1:
                    ip_line_info = str(i + 1) + "\t" + ip_address + "\t此ip主机号为全1\n"
                else:
                    ip_line_info = str(i + 1) + "\t" + ip_address + "\n"
                self.widget_dict_ipv4["text_other_hostseg"].insert(tkinter.END, ip_line_info)
                if i == ip_hostseg:
                    start_index = str(i + 2) + "." + str(len(str(i + 2)))
                    end_index = str(i + 2) + "." + str(len(str(i + 2)) + 1 + len(ip_address))
                    self.widget_dict_ipv4["text_other_hostseg"].tag_add("ip_address_fg", start_index, end_index)
        # 记录当前网段及子网掩码位数
        self.current_netseg = ip_netseg
        self.current_maskint = new_maskint
        self.is_calculated = True
        self.widget_dict_ipv4["sv_input_ip"].set("")
        self.widget_dict_ipv4["sv_input_ip"].set(input_ip_str + "/" + str(new_maskint))

    def calculate_ip_maskint(self, input_ip_maskint_str, maskint=None):
        # 输入信息为 ip/掩码位数，例如 "10.99.1.3/24"
        # maskint如果要赋值，需要赋str类型的值
        self.widget_dict_ipv4["text_ip_base_info"].delete("1.0", tkinter.END)
        ip_maskint_seg_list = input_ip_maskint_str.split("/")
        input_ip_str = ip_maskint_seg_list[0]
        if maskint is None:
            new_maskint = ip_maskint_seg_list[1]
        else:
            new_maskint = maskint
        self.calculate_ip(input_ip_str, new_maskint)

    def calculate_last_netseg(self):
        # 计算上一子网信息
        if not self.is_calculated:
            return
        else:
            self.widget_dict_ipv4["text_ip_base_info"].delete("1.0", tkinter.END)
            current_netseg_int = cofnet.ip_mask_to_int(self.current_netseg)
            shift_bit = 32 - int(self.current_maskint)
            last_netseg = cofnet.int32_to_ip(((current_netseg_int >> shift_bit) - 1) << shift_bit)
            self.calculate_ip(last_netseg, self.current_maskint)

    def calculate_last_cidrv6(self):
        # 计算上一地址块信息
        if not self.is_calculated6:
            return
        else:
            pass

    def calculate_next_netseg(self):
        # 计算下一子网信息
        if not self.is_calculated:
            return
        else:
            self.widget_dict_ipv4["text_ip_base_info"].delete("1.0", tkinter.END)
            current_netseg_int = cofnet.ip_mask_to_int(self.current_netseg)
            shift_bit = 32 - int(self.current_maskint)
            next_netseg = cofnet.int32_to_ip(((current_netseg_int >> shift_bit) + 1) << shift_bit)
            self.calculate_ip(next_netseg, self.current_maskint)

    def calculate_next_cidrv6(self):
        # 计算下一地址块信息
        if not self.is_calculated6:
            return
        else:
            pass

    def calculate_ip_range(self, input_ip_str):
        # 输入信息为 ip-range，例如 "10.99.1.33-55"
        # 需要计算ip默认所属类型，Class A,B,C,D
        ip_address = ""
        maskint = 32
        maskbyte = "255.255.255.255"

    def calculate_ip_range2(self, input_ip_str):
        # 输入信息为 ip-range，例如 "10.99.1.33-10.99.1.55"
        ip_address = ""
        maskint = 32
        maskbyte = "255.255.255.255"

    def calculate_cidr(self, input_ip_str):  # 被前面的 calculate_ip_maskint() 给替代了
        # 输入信息为 cidr，例如 "10.99.1.0/24"
        ip_address = ""
        maskint = 32
        maskbyte = "255.255.255.255"

    def calculate6_ipv6(self, input_ipv6_str: str, ipv6_prefix_len=None):
        """
        输入信息为 ipv6，前缀位数（可选）
        ipv6_prefix_len如果要赋值，需要赋str类型的值
        """
        if ipv6_prefix_len is None:
            new_ipv6_prefix_len = "128"
        else:
            if int(ipv6_prefix_len) < 0 or int(ipv6_prefix_len) > 128:
                messagebox.showinfo("Error", "ipv6前缀位数应该在[0-128]区间内")
                return
            else:
                new_ipv6_prefix_len = ipv6_prefix_len
        self.widget_dict_ipv6["text_ipv6_base_info"].delete("1.0", tkinter.END)
        # 开始计算
        ipv6_address_full = cofnet.convert_to_ipv6_full(input_ipv6_str)
        ipv6_address_short = cofnet.convert_to_ipv6_short(input_ipv6_str)
        ipv6_prefix_cidrv6 = cofnet.get_ipv6_prefix_cidrv6(input_ipv6_str, int(new_ipv6_prefix_len))
        ipv6_address_full_text = f"ipv6地址完全式: {ipv6_address_full}\n"
        ipv6_address_short_text = f"ipv6地址缩写式: {ipv6_address_short}"
        ipv6_prefix_text = f"ipv6地址前缀: {ipv6_prefix_cidrv6}\n"
        # 将ip相关信息输出到Text控件中
        self.widget_dict_ipv6["text_ipv6_base_info"].insert(tkinter.END, ipv6_address_full_text)
        start_index1 = "1.11"
        end_index1 = "1." + str(11 + len(ipv6_address_full))
        self.widget_dict_ipv6["text_ipv6_base_info"].tag_add("ipv6_address_fg", start_index1, end_index1)

        self.widget_dict_ipv6["text_ipv6_base_info"].insert(tkinter.END, ipv6_address_short_text)
        start_index2 = "2.11"
        end_index2 = "2." + str(11 + len(ipv6_address_short))
        self.widget_dict_ipv6["text_ipv6_base_info"].tag_add("ipv6_address_fg", start_index2, end_index2)
        self.widget_dict_ipv6["text_ipv6_base_info"].insert(tkinter.END, "/" + new_ipv6_prefix_len + "\n")

        self.widget_dict_ipv6["text_ipv6_base_info"].insert(tkinter.END, ipv6_prefix_text)
        start_index3 = "3.10"
        end_index3 = "3." + str(10 + len(ipv6_prefix_cidrv6))
        self.widget_dict_ipv6["text_ipv6_base_info"].tag_add("ipv6_address_fg", start_index3, end_index3)
        # 更新子网掩码滑块及spinbox的值
        self.widget_dict_ipv6["sv_ipv6_prefix_len_int"].set(int(new_ipv6_prefix_len))
        self.widget_dict_ipv6["ipv6_prefix_len_scale"].set(int(new_ipv6_prefix_len))
        # 记录当前网段及子网掩码位数
        self.current_ipv6_prefix_cidrv6 = ipv6_prefix_cidrv6
        self.current_ipv6_prefix_len = new_ipv6_prefix_len
        self.is_calculated = True
        self.widget_dict_ipv6["sv_input_ipv6"].set("")
        self.widget_dict_ipv6["sv_input_ipv6"].set(ipv6_address_short + "/" + str(new_ipv6_prefix_len))

    def calculate6_cidrv6(self, ipv6addr_prefix_len_str, ipv6_prefix_len=None):
        # 输入信息为 ipv6/前缀位数，例如 "FD00::11/64"
        # ipv6_prefix_len如果要赋值，需要赋str类型的值
        self.widget_dict_ipv6["text_ipv6_base_info"].delete("1.0", tkinter.END)
        ipv6addr_prefix_len_seg_list = ipv6addr_prefix_len_str.split("/")
        input_ipv6_str = ipv6addr_prefix_len_seg_list[0]
        if ipv6_prefix_len is None:
            new_ipv6_prefix_len = ipv6addr_prefix_len_seg_list[1]
        else:
            new_ipv6_prefix_len = ipv6_prefix_len
        self.calculate6_ipv6(input_ipv6_str, new_ipv6_prefix_len)

    def create_menu_bar_init(self):
        """
        创建菜单栏-主界面的
        创建完菜单栏后，一般不会再修改此组件了
        :return:
        """
        self.menu_bar = tkinter.Menu(self.window_obj)  # 创建一个菜单，做菜单栏
        # 创建一个菜单，做1级子菜单，不分窗（表示此菜单不可拉出来变成一个可移动的独立弹窗）
        menu_help = tkinter.Menu(self.menu_bar, tearoff=0, activebackground="green", activeforeground="white",
                                 background="white", foreground="black")
        # 菜单栏添加1级子菜单
        self.menu_bar.add_cascade(label="Help", menu=menu_help)
        # 1级子菜单添加2级子菜单（功能按钮）
        menu_help.add_command(label="About", command=self.click_menu_about_of_menu_bar_init)
        # 主窗口添加菜单栏
        self.window_obj.config(menu=self.menu_bar)

    def click_menu_about_of_menu_bar_init(self):
        messagebox.showinfo("About", "\n".join(self.about_info_list))

    @staticmethod
    def clear_tkinter_widget(root):
        for widget in root.winfo_children():
            widget.destroy()

    def on_closing_main_window(self):
        print("MainWindow.on_closing_main_window: 退出了主程序")
        # self.window_obj.destroy()
        self.window_obj.quit()


if __name__ == '__main__':
    # 创建程序主界面对象，全局只有一个
    main_window_obj = MainWindow(width=800, height=550, title='ipTool')
    main_window_obj.show()  # 显示主界面，一切从这里开始
