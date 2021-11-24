import sys
import threading
import os
import time
import rpy2.robjects as robjects
from multiprocessing import Process
import multiprocessing

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import tkinter.filedialog


def set_Tk_var():
    global combobox
    combobox = tk.StringVar()

def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top

def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None


def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    set_Tk_var()
    top = Toplevel1(root)
    init(root, top)
    root.protocol('WM_DELETE_WINDOW', top.close_w)
    root.mainloop()


def calculate(mzmlnames, libnames, ppm, fdr, dec_type, fea_ions, ms_data_type):
    import FIGS_Deconvolute
    FIGS_Deconvolute.run(mzmlnames, libnames, ppm=float(ppm), distance=100.0, fdr=float(fdr),
                         dec_type=dec_type, fea_ions=fea_ions,
                         ms_data_type=ms_data_type)
    mzmlname = mzmlnames[0]
    # print('----------------------------------------')
    # print('Start Quant..............')
    # print(mzmlname)
    mzml = str(mzmlname).split('.mzML')[0]
    dirPath = os.path.join(mzml, os.path.basename(str(libnames[0]).split('.blib')[0]) + '_' + str(int(float(ppm))) + 'ppm')

    robjects.r.source('FIGS_Quant.R')
    # r_p1 = Process(target=robjects.r.r_run, args=(mzml, dirPath, float(fdr),))
    # r_p1.start()
    r_th1 = threading.Thread(target=robjects.r.r_run, args=(mzml, dirPath, float(fdr),))
    r_th1.setDaemon(True)  # 守护线程
    r_th1.start()


class Toplevel1:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("579x454+425+131")
        top.minsize(120, 1)
        top.maxsize(1370, 749)
        top.resizable(1, 1)
        top.title("FIGS")
        top.configure(background="#ececec")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.TLabelframe1 = ttk.Labelframe(top)
        self.TLabelframe1.place(relx=0.0, rely=0.0, relheight=0.478
                , relwidth=0.466)
        self.TLabelframe1.configure(relief='')
        self.TLabelframe1.configure(text='''MS data''')

        self.add_data = ttk.Button(self.TLabelframe1)
        self.add_data.place(relx=0.037, rely=0.115, height=27, width=87
                , bordermode='ignore')
        self.add_data.configure(takefocus="")
        self.add_data.configure(text='''Add data''')

        self.clear_data = ttk.Button(self.TLabelframe1)
        self.clear_data.place(relx=0.644, rely=0.115, height=27, width=87
                , bordermode='ignore')
        self.clear_data.configure(takefocus="")
        self.clear_data.configure(text='''Clear data''')

        self.ms_data_files = ScrolledListBox(self.TLabelframe1)
        self.ms_data_files.place(relx=0.037, rely=0.286, relheight=0.553
                , relwidth=0.93, bordermode='ignore')
        self.ms_data_files.configure(background="white")
        self.ms_data_files.configure(cursor="xterm")
        self.ms_data_files.configure(disabledforeground="#a3a3a3")
        self.ms_data_files.configure(font="TkFixedFont")
        self.ms_data_files.configure(foreground="black")
        self.ms_data_files.configure(highlightbackground="#d9d9d9")
        self.ms_data_files.configure(highlightcolor="#d9d9d9")
        self.ms_data_files.configure(selectbackground="#c4c4c4")
        self.ms_data_files.configure(selectforeground="black")

        self.add_library = ttk.Button(self.TLabelframe1)
        self.add_library.place(relx=0.037, rely=0.876, height=27, width=87
                , bordermode='ignore')
        self.add_library.configure(takefocus="")
        self.add_library.configure(text='''Add library''')

        self.lib_path = ttk.Entry(self.TLabelframe1)
        self.lib_path.place(relx=0.37, rely=0.876, relheight=0.106
                , relwidth=0.593, bordermode='ignore')
        self.lib_path.configure(takefocus="")
        self.lib_path.configure(cursor="ibeam")

        self.TLabelframe2 = ttk.Labelframe(top)
        self.TLabelframe2.place(relx=0.0, rely=0.485, relheight=0.522
                , relwidth=0.466)
        self.TLabelframe2.configure(relief='')
        self.TLabelframe2.configure(text='''Parameters''')

        self.TLabel1 = ttk.Label(self.TLabelframe2)
        self.TLabel1.place(relx=0.037, rely=0.08, height=35, width=37
                , bordermode='ignore')
        self.TLabel1.configure(background="#d9d9d9")
        self.TLabel1.configure(foreground="#000000")
        self.TLabel1.configure(font="TkDefaultFont")
        self.TLabel1.configure(relief="flat")
        self.TLabel1.configure(anchor='w')
        self.TLabel1.configure(justify='left')
        self.TLabel1.configure(text='''PPM''')

        self.TLabel2 = ttk.Label(self.TLabelframe2)
        self.TLabel2.place(relx=0.037, rely=0.245, height=34, width=37
                , bordermode='ignore')
        self.TLabel2.configure(background="#d9d9d9")
        self.TLabel2.configure(foreground="#000000")
        self.TLabel2.configure(font="TkDefaultFont")
        self.TLabel2.configure(relief="flat")
        self.TLabel2.configure(anchor='w')
        self.TLabel2.configure(justify='left')
        self.TLabel2.configure(text='''FDR''')

        self.TLabel3 = ttk.Label(self.TLabelframe2)
        self.TLabel3.place(relx=0.037, rely=0.405, height=34, width=96
                , bordermode='ignore')
        self.TLabel3.configure(background="#d9d9d9")
        self.TLabel3.configure(foreground="#000000")
        self.TLabel3.configure(font="TkDefaultFont")
        self.TLabel3.configure(relief="flat")
        self.TLabel3.configure(anchor='w')
        self.TLabel3.configure(justify='left')
        self.TLabel3.configure(text='''Decoration type''')

        self.TLabel4 = ttk.Label(self.TLabelframe2)
        self.TLabel4.place(relx=0.037, rely=0.565, height=35, width=86
                , bordermode='ignore')
        self.TLabel4.configure(background="#d9d9d9")
        self.TLabel4.configure(foreground="#000000")
        self.TLabel4.configure(font="TkDefaultFont")
        self.TLabel4.configure(relief="flat")
        self.TLabel4.configure(anchor='w')
        self.TLabel4.configure(justify='left')
        self.TLabel4.configure(text='''Featured-ions''')

        self.TLabel5 = ttk.Label(self.TLabelframe2)
        self.TLabel5.place(relx=0.037, rely=0.73, height=34, width=95
                , bordermode='ignore')
        self.TLabel5.configure(background="#d9d9d9")
        self.TLabel5.configure(foreground="#000000")
        self.TLabel5.configure(font="TkDefaultFont")
        self.TLabel5.configure(relief="flat")
        self.TLabel5.configure(anchor='w')
        self.TLabel5.configure(justify='left')
        self.TLabel5.configure(text='''MS data type''')

        self.fdr = ttk.Entry(self.TLabelframe2)
        self.fdr.place(relx=0.178, rely=0.283, relheight=0.093, relwidth=0.807
                , bordermode='ignore')
        self.fdr.configure(takefocus="")
        self.fdr.configure(cursor="ibeam")

        self.fea_ions = ttk.Combobox(self.TLabelframe2)
        self.fea_ions.place(relx=0.356, rely=0.608, relheight=0.093
                , relwidth=0.619, bordermode='ignore')
        self.fea_ions.configure(takefocus="")

        self.ms_data_type = ttk.Combobox(self.TLabelframe2)
        self.ms_data_type.place(relx=0.356, rely=0.768, relheight=0.093
                , relwidth=0.619, bordermode='ignore')
        self.ms_data_type.configure(takefocus="")

        self.ppm = ttk.Entry(self.TLabelframe2)
        self.ppm.place(relx=0.178, rely=0.122, relheight=0.093, relwidth=0.807
                , bordermode='ignore')
        self.ppm.configure(takefocus="")
        self.ppm.configure(cursor="ibeam")

        self.dec_type = ttk.Combobox(self.TLabelframe2)
        self.dec_type.place(relx=0.393, rely=0.443, relheight=0.097
                , relwidth=0.593, bordermode='ignore')
        self.dec_type.configure(takefocus="")

        self.TLabelframe3 = ttk.Labelframe(top)
        self.TLabelframe3.place(relx=0.484, rely=0.11, relheight=0.879
                , relwidth=0.516)
        self.TLabelframe3.configure(relief='')
        self.TLabelframe3.configure(text='''Log''')

        self.log_out = ScrolledListBox(self.TLabelframe3)
        self.log_out.place(relx=0.033, rely=0.05, relheight=0.9, relwidth=0.936
                , bordermode='ignore')
        self.log_out.configure(background="white")
        self.log_out.configure(cursor="xterm")
        self.log_out.configure(disabledforeground="#a3a3a3")
        self.log_out.configure(font="TkFixedFont")
        self.log_out.configure(foreground="black")
        self.log_out.configure(highlightbackground="#d9d9d9")
        self.log_out.configure(highlightcolor="#d9d9d9")
        self.log_out.configure(selectbackground="#c4c4c4")
        self.log_out.configure(selectforeground="black")

        self.run = ttk.Button(top)
        self.run.place(relx=0.484, rely=0.044, height=27, width=87)
        self.run.configure(takefocus="")
        self.run.configure(text='''Run''')

        self.stop = ttk.Button(top)
        self.stop.place(relx=0.832, rely=0.044, height=27, width=87)
        self.stop.configure(takefocus="")
        self.stop.configure(text='''Stop''')

        self.menubar = tk.Menu(top,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        top.configure(menu = self.menubar)

        """event"""
        self.add_data.bind('<Button-1>', self.add_ms_data)
        self.clear_data.bind('<Button-1>', self.clear_ms_data)
        self.add_library.bind('<Button-1>', self.add_library_data)
        self.run.bind('<Button-1>', self.run_start)
        self.stop.bind('<Button-1>', self.run_stop)

        """parameter"""
        self.log_thread = False  # log输出线程是否已在执行
        self.cal_thread = False  # python计算进程是否已在执行
        self.r_process = []  # 保存r语言多进程
        self.py_process = []  # 保存python语言多进程

        self.ppm.insert(0, "20")
        self.fdr.insert(0, "0.01")
        self.dec_type['value'] = ["Default"]
        self.dec_type.set("Default")
        #self.dec_type.configure(state="disabled")  # 设置状态为禁用
        self.dec_type.configure(state="readonly")  # 设置状态为只读
        self.fea_ions['value'] = ["Default", "Top10-first"]
        self.fea_ions.set("Default")
        self.fea_ions.configure(state="readonly")  # 设置状态为只读
        # self.fea_ions.configure(state="disabled")  # 设置状态为禁用
        self.ms_data_type['value'] = ["DIA", "RT-free(retain)"]
        self.ms_data_type.set("DIA")
        self.ms_data_type.configure(state="readonly")

    def write(self, out_stream):
        if str(out_stream) != '\n' and str(out_stream) != " ":
            self.log_out.insert('end', str(out_stream))

    def add_ms_data(self, event):
        filenames = tkinter.filedialog.askopenfilenames()
        if len(filenames) != 0:
            del_text_index = -1
            for i in range(self.ms_data_files.size_()):
                if self.ms_data_files.get(i) == 'You did not select any files!':
                    del_text_index = i
                    break
            if del_text_index != -1:
                self.ms_data_files.delete(del_text_index)
            files = list(self.ms_data_files.get(0, 'end'))
            files.extend(filenames)
            files = list(set(files))
            self.ms_data_files.delete(0, 'end')
            for i in range(len(files)):
                self.ms_data_files.insert(0, str(files[i]))
        else:
            del_text_index = -1
            for i in range(self.ms_data_files.size_()):
                if self.ms_data_files.get(i) == 'You did not select any files!':
                    del_text_index = i
                    break
            if del_text_index != -1:
                self.ms_data_files.delete(del_text_index)
            if self.ms_data_files.size_() == 0:
                self.ms_data_files.insert(0, "You did not select any files!")

    def clear_ms_data(self, event):
        self.ms_data_files.delete(0, self.ms_data_files.size_())

    def add_library_data(self, event):
        self.lib_path.delete(0, 'end')
        filename = tkinter.filedialog.askopenfilename()
        if filename != '':
            self.lib_path.insert(0, filename)
        else:
            self.lib_path.insert(0, "You did not select any files!")

    def run_status(self):  # 判断是否有进程在运行
        all_process = []
        for i in self.py_process:
            all_process.append(i.is_alive())
        # print(all_process)
        for i in all_process:
            if i:
                return True  # 仍在运行
        return False  # 没有进程在运行

    def r_print(self):
        with open('log.txt', 'w'):
            pass
        line_print = 0
        while True:
            time.sleep(2)
            count_line = 0
            stoped = False
            with open('log.txt', 'r') as r:
                for line in r:
                    count_line += 1
                    if count_line > line_print:
                        self.log_out.insert('end', line)
                        line_print += 1
                        if line.startswith("end"):  # 出现end说明计算执行完毕
                            stoped = True
            if stoped:
                time.sleep(2)  # 给进程终止的时间
                if self.run_status():  # 如果还未终止，再加3秒
                    time.sleep(3)
                if not self.run_status():  # 所有进程已终止
                    print('----------------------------------------')
                    print(time.strftime("stop time: %Y-%m-%d %H:%M:%S", time.localtime()))
                    print("total time: %s minutes" % format((time.time() - self.start_time)/60, ".2f"))

    def run_stop(self, event):
        for py_pro in self.py_process:
            if py_pro.is_alive():
                py_pro.terminate()
                py_pro.join()
        # python = sys.executable
        # os.execl(python, python, * sys.argv)
        print('! ! !Stoped! ! !')

    def close_w(self):
        for py_pro in self.py_process:
            if py_pro.is_alive():
                py_pro.terminate()
                py_pro.join()
        root.destroy()

    def run_calculate(self):
        mzmlnames = self.ms_data_files.get(0, 'end')
        libnames = [''.join(list(self.lib_path.get()))]
        print('----------------------------------------')
        print('Mass spectrometry data:', mzmlnames)
        print('Library file:', libnames)
        print('---------------Parameters---------------')
        print('PPM:', self.ppm.get())
        print('FDR:', self.fdr.get())
        print('Decoration type:', self.dec_type.get())
        print('Featured-ions:', self.fea_ions.get())
        print('MS data type:', self.ms_data_type.get())
        print('----------------------------------------')
        print("Start calculate..........")
        if not self.log_thread:
            th2 = threading.Thread(target=self.r_print)
            th2.setDaemon(True)  # 守护线程
            th2.start()
            self.th2 = th2
            self.log_thread = True

        # 格式化成2016-03-20 11:45:39形式
        print(time.strftime("start time: %Y-%m-%d %H:%M:%S", time.localtime()))
        self.start_time = time.time()
        print('----------------------------------------')
        for mzml in mzmlnames:
            py_p1 = Process(target=calculate, args=([mzml], libnames, self.ppm.get(), self.fdr.get(),
                                            self.dec_type.get(), self.fea_ions.get(), self.ms_data_type.get(),))
            py_p1.start()
            self.py_process.append(py_p1)

    def run_start(self, event):
        run_s = False
        current = sys.stdout  # 将当前系统输出储存到临时变量
        a = self
        sys.stdout = a
        mzmlnames = self.ms_data_files.get(0, 'end')
        libnames = [''.join(list(self.lib_path.get()))]
        if len(mzmlnames) == 0:
            print('You did not select mass spectrometry data!')
        elif len(mzmlnames) == 1 and self.ms_data_files.get(0) == "You did not select any files!":
            print('You did not select mass spectrometry data!')
        elif not str(mzmlnames[0]).endswith(".mzML") and not str(mzmlnames[0]).endswith(".mzml"):
            print("Please select a file in .mzML format!")
        else:
            if len(libnames) == 1 and libnames[0] != "" and libnames[0] != "You did not select any files!":
                if str(libnames[0]).endswith('.blib'):
                    run_s = True
                else:
                    print("Please select a file in .blib format!")
            else:
                print('You did not select a library file!')
        if run_s:
            if not self.cal_thread:
                self.run_calculate()
                self.cal_thread = True
            else:
                still_cal = False  # 现在是否有线程或进程还在计算
                all_process = []
                for i in self.py_process:
                    all_process.append(i.is_alive())
                # print(all_process)
                for i in all_process:
                    if i:
                        still_cal = True
                if still_cal:
                    print('! ! !Please stop it before starting a new calculation! ! !')
                else:
                    self.cal_thread = False
                    print('----------------------------------------')
                    print('! ! !Start a new calculation! ! !')
                    # self.py_process = []
                    self.run_start(event)
        # sys.stdout = current


# The following code is added to facilitate the Scrolled widgets you specified.
class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''
    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))
        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        # Copy geometry methods of master  (taken from ScrolledText.py)
        if py3:
            methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
                  | tk.Place.__dict__.keys()
        else:
            methods = tk.Pack.__dict__.keys() + tk.Grid.__dict__.keys() \
                  + tk.Place.__dict__.keys()
        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)


def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
        container.bind('<Leave>', lambda e: _unbound_to_mousewheel(e, container))
        return func(cls, container, **kw)
    return wrapped

class ScrolledListBox(AutoScroll, tk.Listbox):
    '''A standard Tkinter Listbox widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        tk.Listbox.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)
    def size_(self):
        sz = tk.Listbox.size(self)
        return sz

import platform
def _bound_to_mousewheel(event, widget):
    child = widget.winfo_children()[0]
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-MouseWheel>', lambda e: _on_shiftmouse(e, child))
    else:
        child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
        child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))


def _unbound_to_mousewheel(event, widget):
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        widget.unbind_all('<MouseWheel>')
        widget.unbind_all('<Shift-MouseWheel>')
    else:
        widget.unbind_all('<Button-4>')
        widget.unbind_all('<Button-5>')
        widget.unbind_all('<Shift-Button-4>')
        widget.unbind_all('<Shift-Button-5>')


def _on_mousewheel(event, widget):
    if platform.system() == 'Windows':
        widget.yview_scroll(-1*int(event.delta/120),'units')
    elif platform.system() == 'Darwin':
        widget.yview_scroll(-1*int(event.delta),'units')
    else:
        if event.num == 4:
            widget.yview_scroll(-1, 'units')
        elif event.num == 5:
            widget.yview_scroll(1, 'units')


def _on_shiftmouse(event, widget):
    if platform.system() == 'Windows':
        widget.xview_scroll(-1*int(event.delta/120), 'units')
    elif platform.system() == 'Darwin':
        widget.xview_scroll(-1*int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.xview_scroll(-1, 'units')
        elif event.num == 5:
            widget.xview_scroll(1, 'units')


if __name__ == '__main__':
    multiprocessing.freeze_support()
    vp_start_gui()
