import threading
import time
import tkinter as tk
from tkinter import Toplevel, PhotoImage
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import asksaveasfilename


class ttlog(ScrolledText):
    """readonly scrolled text log class"""
    def __init__(self, **kw):
        # state=tk.DISABLED,
        super().__init__(**kw, cursor='plus',
                         wrap=tk.WORD, font=('monospace', 12))
        self.tag_config('TITLE', foreground='blue')
        self.tag_config('INFO', foreground='black')
        self.tag_config('DEBUG', foreground='gray')
        self.tag_config('WARNING', foreground='orange')
        self.tag_config('ERROR', foreground='red')
        self.tag_config('CRITICAL', foreground='red', underline=1)
        self.rpop = tk.Menu(self, tearoff=0)
        self.rpop.add_command(label='Export', command=self._copyas)
        self.rpop.add_command(label='Copy', command=self._copyto)
        self.rpop.add_command(label='Clean', command=self.clean)
        self.bind('<Button-3>', self._popup)
        self.bind('<Button-1>', self._popdown)
        self.bind('<Up>', self._lineUp)
        self.bind('<Down>', self._lineDown)
        self.pList = []
        self.thread = ttlog_thread(self)
        self.thread.setDaemon(True)
        self.thread.start()

    def _popup(self, event):
        self.rpop.post(event.x_root, event.y_root)

    def _popdown(self, event):
        self.rpop.unpost()
        self.focus_set()

    def _copyas(self):
        saveTo = asksaveasfilename()
        if not isinstance(saveTo, str): return
        if saveTo == '': return
        with open(saveTo, 'w') as f:
            f.write(self.get('1.0', tk.END))

    def _copyto(self):
        self.clipboard_clear()
        try:
            selection = self.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass  # skip TclError while no selection
        else:
            self.clipboard_append(selection)

    def title(self, content, end='\n'):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, content + end, 'TITLE')
        self.see(tk.END)
        self.config(state=tk.DISABLED)

    def _log(self, content, end='\n'):
        content=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+":\t\t\t"+content
        self.insert(tk.END, content + end, 'INFO')
        # self.see(tk.END)

    def start_log(self):
        self.config(state=tk.NORMAL)
        self.thread.resume()

    def end_log(self):
        self.thread.pause()

    def stop_log(self):
        self.thread.stop()

    def log(self, content, end='\n'):  # the name 'info' is not allowed
        content=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+":\t\t\t"+content
        self.insert(tk.END, content + end, 'INFO')


    def debug(self, content, end='\n'):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, content + end, 'DEBUG')
        self.see(tk.END)
        self.config(state=tk.DISABLED)

    def warning(self, content, end='\n'):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, content + end, 'WARNING')
        self.see(tk.END)
        self.config(state=tk.DISABLED)

    def error(self, content, end='\n'):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, content + end, 'ERROR')
        self.see(tk.END)
        self.config(state=tk.DISABLED)

    def critical(self, content, end='\n'):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, content + end, 'CRITICAL')
        self.see(tk.END)
        self.config(state=tk.DISABLED)

    def png(self, pngFile):
        try:
            self.pList.append(PhotoImage(file=pngFile))
            self.image_create(tk.END,
                              image=self.pList[len(self.pList) - 1])
            self.log('')
        except Exception as e:
            self.debug(repr(e))

    def gif(self, gifFile):
        try:
            self.pList.append(PhotoImage(file=gifFile))
            self.image_create(tk.END,
                              image=self.pList[len(self.pList) - 1])
            self.log('')
        except Exception as e:
            self.debug(repr(e))

    def _lineUp(self, event):
        self.yview('scroll', -1, 'units')

    def _lineDown(self, event):
        self.yview('scroll', 1, 'units')

    def clean(self):
        self.config(state=tk.NORMAL)
        self.delete('1.0', tk.END)
        self.pList.clear()
        self.config(state=tk.DISABLED)

class ttlog_thread(threading.Thread):
    def __init__(self,ttlog, *args, **kwargs):
        super(ttlog_thread, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()  # 用于暂停线程的标识,Event默认内置了一个标志，初始值为False
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True
        self.ttlog=ttlog

    def run(self):
        while self.__running.isSet():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            time.sleep(1)
            print(11111)
            self.ttlog.see(tk.END)

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞
