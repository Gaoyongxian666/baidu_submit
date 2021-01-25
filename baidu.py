import base64
import datetime
import json
import multiprocessing
import os
import re
import time
import tkinter as tk
import tkinter.messagebox
import traceback
import webbrowser
from multiprocessing.dummy import Pool as ThreadPool
from threading import Thread
from tkinter import ttk
from tkinter.ttk import Scrollbar

import requests
from sqlitedict import SqliteDict

from tklog import tklog
from ttlog import ttlog
from icon import img



class Main_window(object):
    """主窗体"""

    def __init__(self, title, icon):
        self.root = tk.Tk()
        self.root.title(title)
        win_width = self.root.winfo_screenwidth()
        win_higth = self.root.winfo_screenheight()
        width_adjust = (win_width - 1000) / 2
        higth_adjust = (win_higth - 600) / 2
        self.root.geometry("%dx%d+%d+%d" % (1000, 600, width_adjust, higth_adjust))
        if os.path.exists(icon):
            print("存在:不需要创建")
        else:
            print("不存在:需要创建")

            tmp = open(icon, "wb+")
            tmp.write(base64.b64decode(img))
            tmp.close()
        self.root.iconbitmap(icon)

        # 日志
        self.eblog = tklog(master=self.root)
        self.eblog.place(x=50, y=380, width=905, height=200)

        # 填写域名等
        self.site = tk.Label(self.root, text="网站域名:")
        self.site.place(x=50, y=30, )
        self.site_entrytext = tk.Entry(self.root)
        self.site_entrytext.place(x=130, y=30, width=300, heigh=20)
        self.token = tk.Label(self.root, text="Token:")
        self.token.place(x=50, y=60, )
        self.token_entrytext = tk.Entry(self.root)
        self.token_entrytext.place(x=130, y=60, width=300, heigh=20)
        self.sitemap = tk.Label(self.root, text="Sitemap地址:")
        self.sitemap.place(x=50, y=90, )
        self.sitemap_entrytext = tk.Entry(self.root)
        self.sitemap_entrytext.place(x=130, y=90, width=300, heigh=20)
        self.notice = tk.Label(self.root, text="域名地址要完整(带https://)，Token在百度站长平台获取，Sitemap写网络地址。")
        self.notice.place(x=50, y=120, )


        # Button按钮
        self.quick_button = tk.Button(self.root, text="快速收录", command=lambda: self.quick(self.site_entrytext.get(),self.token_entrytext.get(),self.sitemap_entrytext.get()))
        self.quick_button.place(x=500, y=30, heigh=45)

        self.ordinary_button = tk.Button(self.root, text="普通收录", command=lambda: self.ordinary(self.site_entrytext.get(),self.token_entrytext.get(),self.sitemap_entrytext.get()))
        self.ordinary_button.place(x=600, y=30, heigh=45)

        self.save_button = tk.Button(self.root, text="保存配置",command=lambda: self.save(self.site_entrytext.get(), self.token_entrytext.get(),self.sitemap_entrytext.get()))
        self.save_button.place(x=700, y=30, heigh=45)

        self.quick_reset_button = tk.Button(self.root, text="快速收录重置", command=self.quick_reset)
        self.quick_reset_button.place(x=500, y=90, heigh=45)

        self.ordinary_reset_button = tk.Button(self.root, text="普通收录重置",command=self.ordinary_reset)
        self.ordinary_reset_button.place(x=600, y=90, heigh=45)

        self.update_button = tk.Button(self.root, text="更新Sitemap",command=lambda: self.update(self.sitemap_entrytext.get()))
        self.update_button.place(x=700, y=90, heigh=45)

        self.update_button = tk.Button(self.root, text="Github",
                                       command=self.click)
        self.update_button.place(x=800, y=90, heigh=45)


        # 列表
        self.frame = tk.Frame(self.root)
        self.frame.place(x=50, y=150, width=900, height=210)
        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side="right", fill="y")
        self.tree = ttk.Treeview(self.root, yscrollcommand=self.scrollbar.set)
        self.tree.place(x=50, y=150, width=880, heigh=210)
        self.tree["show"] = "headings"
        self.tree["columns"] = ("地址", "普通收录状态","快速收录状态", "添加时间")
        self.tree.column("地址", width=335)
        self.tree.column("普通收录状态", width=50)
        self.tree.column("快速收录状态", width=50)
        self.tree.column("添加时间", width=50)
        self.tree.heading("地址", text="地址")
        self.tree.heading("普通收录状态", text="普通收录状态")
        self.tree.heading("快速收录状态", text="快速收录状态")
        self.tree.heading("添加时间", text="添加时间")
        self.scrollbar.config(command=self.tree.yview)

        # 是否加载列表？
        flag = tk.messagebox.askquestion("加载列表", "是否加载本地列表？\n尽量选“是”，但选“否”不会影响，只是不会展示本地的sitemap信息。\n如果链接数量过万，可能需要加载一分钟")
        if flag == "yes":
            Tree_control(self.tree, self.eblog)
        else:
            self.eblog.log("你选择了否，没有加载本地列表")

        # 设置关闭
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # 加载配置文件
        if os.path.exists("setting.txt"):
            with open("setting.txt","r",encoding="utf8")as f:
                setting_dict=eval(f.readline())
                self.site_entrytext.insert(0,setting_dict["site"])
                self.token_entrytext.insert(0,setting_dict["token"])
                self.sitemap_entrytext.insert(0,setting_dict["sitemap"])



        self.root.mainloop()

    def click(self):
        webbrowser.open("https://github.com/Gaoyongxian666/baidu_submit")

    def close(self):
        self.root.destroy()

    # 快速收录重置
    def quick_reset(self):
        Wait_window(self.tree,2)

    # 普通收录重置
    def ordinary_reset(self):
        Wait_window(self.tree,1)

    # 保存配置文件
    def save(self, site, token, sitemap):
        with open("setting.txt","w") as f:
            f.write(str({'site':site,'token':token,'sitemap':sitemap}))
            self.eblog.log("配置文件，已经保存。")

    # 普通收录
    def ordinary(self, site, token, sitemap):
        if len(sitemap) == 0 or sitemap is None or sitemap.isspace():
            self.eblog.log("sitemap不能为空")
        elif len(site) == 0 or site is None or site.isspace():
            self.eblog.log("site不能为空")
        elif len(token) == 0 or token is None or token.isspace():
            self.eblog.log("token不能为空")
        else:
            if os.path.exists("sitemap.xml"):
                Baidu_ordinary_windows(self.tree,site,token)
            else:
                tk.messagebox.showinfo("提示", "本地没有检测到sitemap.xml,请先点击更新sitemap")
                self.eblog.log("本地没有检测到sitemap.xml,请先点击更新sitemap")

    # 快速收录
    def quick(self, site, token, sitemap):
        if len(sitemap) == 0 or sitemap is None or sitemap.isspace():
            self.eblog.log("sitemap不能为空")
        elif len(site) == 0 or site is None or site.isspace():
            self.eblog.log("site不能为空")
        elif len(token) == 0 or token is None or token.isspace():
            self.eblog.log("token不能为空")
        else:
            if os.path.exists("sitemap.xml"):
                Baidu_quick_windows(self.tree,site,token)
            else:
                tk.messagebox.showinfo("提示", "本地没有检测到sitemap.xml,请先点击更新sitemap")
                self.eblog.log("本地没有检测到sitemap.xml,请先点击更新sitemap")

    # 更新sitemap
    def update(self, sitemap):
        if len(sitemap) == 0 or sitemap is None or sitemap.isspace():
            self.eblog.log("sitemap不能为空")
        elif os.path.exists("sitemap.xml"):
            flag = tk.messagebox.askquestion("更新", "本地存在Sitemap.xml,如果没有更新可以不下载,是否下载？")
            if flag == "yes":
                Update_window(self.tree, self.eblog, sitemap)
            else:
                self.eblog.log("你选择了否，Sitemap.xml没有更新")
        else:
            Update_window(self.tree, self.eblog, sitemap)



class Update_window(object):
    """sitemap更新窗体"""

    def __init__(self, tree, eblog, sitemap):
        self.newroot = tk.Toplevel()
        self.newroot.title('下载文件中')
        self.newroot.iconbitmap("favicon.ico")
        self.newroot.wm_attributes('-topmost', 1)
        win_width = self.newroot.winfo_screenwidth()
        win_higth = self.newroot.winfo_screenheight()
        width_adjust = (win_width - 400) / 2
        higth_adjust = (win_higth - 250) / 2
        self.newroot.geometry("%dx%d+%d+%d" % (400, 250, width_adjust, higth_adjust))

        # 进度条
        self.bar = ttk.Progressbar(self.newroot, length=300, mode="indeterminate",orient=tk.HORIZONTAL)
        self.bar.pack(expand=True)
        self.bar.start(10)

        # 提示内容
        self.content = tk.Label(self.newroot, text="正在下载Sitemap.xml文件...")
        self.content.place(x=50, y=30, )
        self.content2 = tk.Label(self.newroot, text="下载速度和文件大小以及服务器带宽有关，请耐心等待......")
        self.content2.place(x=50, y=60, )

        self.eblog = eblog
        self.sitemap = sitemap
        self.tree = tree

        # 开启处理线程
        self.p = Thread(target=self.update)
        self.p.setDaemon(True)
        self.p.start()
        self.eblog.log("Sitemap线程：开启sitemap线程,下载Sitemap.xml中...")

        # 关闭右上角
        self.newroot.protocol("WM_DELETE_WINDOW", self.close)

    # 列表添加item,返回iid
    def append_item(self, item_list):
        # 加最后/加前面都可以，因为要是前面iid全是1
        item = self.tree.insert("", 0, values=(item_list[0], item_list[1], item_list[2],item_list[3]))
        return item

    # 处理函数
    def update(self):
        try:
            with open("sitemap.xml", "wb") as f:
                f.write(requests.get(self.sitemap).content)
            with open("sitemap.xml", 'r', encoding='utf-8') as f:
                xml_data = f.read()
            self.content.configure(text="Sitemap文件下载完成，解析快慢与文件大小有关")
            urls = re.findall(r'<loc>(.+?)</loc>', xml_data, re.S)
            self.eblog.log("Sitemap线程：下载Sitemap.xml完成,正在解析xml文件...")

            # 删除所有
            mydict = SqliteDict('./my_db.sqlite', autocommit=True)
            mydict.clear()
            x = self.tree.get_children()
            for item in x:
                self.tree.delete(item)

            # 重新解析
            len_items = len(urls)
            i = 0
            for url in urls:
                i = i + 1
                self.content2.config(text="当前正处理：第" + str(i) + "个，共有" + str(len_items) + "个链接")
                cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                iid = self.append_item([url, "未提交","未提交", cur_time])
                mydict[url] = [url, "未提交","未提交", cur_time, iid]
            self.eblog.log("Sitemap线程：关闭sitemap线程,更新完成。")
            self.close()
        except:
            self.eblog.log(traceback.format_exc())
            self.eblog.log("Sitemap线程：更新失败")

    def close(self):
        self.newroot.destroy()


class Tree_control(object):
    """列表加载窗体"""

    def __init__(self, tree,eblog):
        self.newroot = tk.Toplevel()
        self.newroot.title('加载列表')
        self.newroot.iconbitmap("favicon.ico")
        self.newroot.wm_attributes('-topmost', 1)
        win_width = self.newroot.winfo_screenwidth()
        win_higth = self.newroot.winfo_screenheight()
        width_adjust = (win_width - 400) / 2
        higth_adjust = (win_higth - 250) / 2
        self.newroot.geometry("%dx%d+%d+%d" % (400, 250, width_adjust, higth_adjust))

        # 进度条
        self.__showFlag = True
        self.__width = 300
        self.__heigth = 20
        self.__sleep = 0
        self.bar = ttk.Progressbar(self.newroot, length=self.__width, mode="indeterminate",orient=tk.HORIZONTAL)
        self.bar.pack(expand=True)
        self.bar.start(10)

        # 提示内容
        self.content2 = tk.Label(self.newroot, text="正在加载列表中,请不要中断操作，请耐心等待......")
        self.content2.place(x=50, y=30, )
        self.content = tk.Label(self.newroot, text="")
        self.content.place(x=50, y=60, )
        self.eblog = eblog
        self.tree = tree
        self.mydict = SqliteDict('./my_db.sqlite', autocommit=True)

        # 开启处理线程
        self.p = Thread(target=self.add_item)
        self.p.setDaemon(True)
        self.p.start()

        # 点击关闭右上角
        self.newroot.protocol("WM_DELETE_WINDOW", self.close)

    # 加载item
    def add_item(self):
        len_items=len(sorted(self.mydict.iteritems()))
        i=0
        for key, value in sorted(self.mydict.iteritems()):
            i=i+1
            self.content.config(text="当前正处理：第"+str(i)+"个，共有"+str(len_items)+"个链接")
            self.tree.insert("", 0, iid=value[4], values=(value[0], value[1], value[2],value[3]))
        self.close()
        return 1

    def close(self):
        self.newroot.destroy()


class Baidu_quick_windows(object):
    """百度快速收录窗体"""

    def __init__(self,tree,site,token):
        self.newroot = tk.Toplevel()
        self.newroot.title('快速收录')
        self.newroot.iconbitmap("favicon.ico")
        self.newroot.wm_attributes('-topmost', 1)
        win_width = self.newroot.winfo_screenwidth()
        win_higth = self.newroot.winfo_screenheight()
        width_adjust = (win_width - 800) / 2
        higth_adjust = (win_higth - 250) / 2
        self.newroot.geometry("%dx%d+%d+%d" % (800, 250, width_adjust, higth_adjust))

        # 窗体日志
        self.ttlog = ttlog(master=self.newroot)
        self.ttlog.place(x=10, y=70, width=780, height=150)

        # 提示内容
        self.content = tk.Label(self.newroot, text="正在快速收录中,请不要中断操作，请耐心等待......")
        self.content.place(x=10, y=30, )
        self.content2 = tk.Label(self.newroot, text="")
        self.content2.place(x=10, y=60, )

        self.tree = tree
        self.site=site
        self.token=token
        self.mydict = SqliteDict('./my_db.sqlite', autocommit=True)

        # 开启处理线程
        self.p = Thread(target=self.main)
        self.p.setDaemon(True)
        self.p.start()
        self.ttlog.log("快速收录-->开启普通收录线程.....")

        # 点击关闭右上角
        self.newroot.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        self.newroot.destroy()

    # 获取未提交的数量
    def get_url(self):
        url_list=[]
        mydict = SqliteDict('./my_db.sqlite', autocommit=True)
        for key, value in sorted(mydict.iteritems()):
            if value[2]=="未提交":
                url_list.append(value)
        self.ttlog.log("快速收录-->共有没推送的网页链接数 ：{} 条!".format(len(url_list)))
        print("共有没快速收录推送的网页链接数 ：{} 条!".format(len(url_list)))
        return url_list

    # 提交urls
    def api(self, url):
        post_url = "http://data.zz.baidu.com/urls?site={}&token={}&type=daily".format(self.site, self.token)
        headers = {
            'User-Agent': 'curl/7.12.1',
            'Host': 'data.zz.baidu.com',
            'Content-Type': 'text/plain',
            'Content-Length': '83',
        }
        response = requests.post(post_url, headers=headers, data=url[0])
        req = response.text
        if "success" in req:
            req_json = json.loads(req)
            if req_json["remain"] == 0:
                self.ttlog.log("快速收录-->今天普通收录推送任务已经完成,当天剩余的可推送url条数: 0条。")
            else:
                # 是否修改列表，看是否加载列表
                tree_len = len(self.tree.get_children())
                if tree_len!=0:
                    print("快速收录-->修改列表")
                    self.tree.item(url[4],value=(url[0],url[1],"已提交",url[3]))
                self.mydict[url[0]]=[url[0],url[1],"已提交",url[3],url[4]]
                self.ttlog.log("快速收录-->推送成功：" + url[0] + '\n当天剩余的可推送url条数: {}条'.format(req_json["remain"]))
        else:
            req_json = json.loads(req)
            self.ttlog.log(r"快速收录-->推送失败:" + req_json["message"] + "，即当天可剩余推送数量为0条。")
        return None

    # 处理函数
    def main(self):
        urls = self.get_url()
        post_urls = urls[:10]
        try:
            cpu_num = multiprocessing.cpu_count()
            self.ttlog.log("CPU核心数：" + str(cpu_num))
            self.ttlog.log("开启线程池，能一定程度加速")
            pool = ThreadPool(cpu_num)
            results = pool.map(self.api, post_urls)
            pool.close()
            pool.join()
            self.ttlog.stop_log()
            self.ttlog.log("快速收录-->今日的推送任务完成！")
            self.content.config(text="普通收录-->今日的推送任务完成！")
        except Exception as e:
            self.ttlog.log('错误代码：{}'.format(e))
            self.ttlog.log("Error: unable to start thread")


class Baidu_ordinary_windows(object):
    """百度普通收录窗体"""

    def __init__(self, tree, site, token):
        # 展示等待窗体
        self.newroot = tk.Toplevel()
        self.newroot.title('普通收录')
        self.newroot.iconbitmap("favicon.ico")
        win_width = self.newroot.winfo_screenwidth()
        win_higth = self.newroot.winfo_screenheight()
        width_adjust = (win_width - 800) / 2
        higth_adjust = (win_higth - 250) / 2
        self.newroot.geometry("%dx%d+%d+%d" % (800, 250, width_adjust, higth_adjust))

        # 提示内容
        self.content = tk.Label(self.newroot, text="正在普通收录中,请不要中断操作，请耐心等待......")
        self.content.place(x=10, y=30, )
        self.content2 = tk.Label(self.newroot, text="")
        self.content2.place(x=10, y=60, )

        # 窗体日志
        self.ttlog = ttlog(master=self.newroot)
        self.ttlog.place(x=10, y=70, width=780, height=150)
        self.tree = tree
        self.site = site
        self.token = token
        self.mydict = SqliteDict('./my_db.sqlite', autocommit=True)

        # 开始处理线程
        self.p = Thread(target=self.main)
        self.p.setDaemon(True)
        self.p.start()
        self.ttlog.log("普通收录-->开启普通收录线程.....")

        # 点击关闭右上角
        self.newroot.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        self.ttlog.stop_log()
        self.newroot.destroy()

    # 获取未提交的urls
    def get_url(self):
        url_list = []
        for key, value in sorted(self.mydict.iteritems()):
            if value[1] == "未提交":
                url_list.append(value)
        self.ttlog.log("普通收录-->共有没推送的网页链接数 ：{} 条!".format(len(url_list)))
        print("共有没普通收录推送的网页链接数 ：{} 条!".format(len(url_list)))
        return url_list

    # 查询剩余次数
    def get_remain(self):
        post_url = "http://data.zz.baidu.com/urls?site={}&token={}".format(self.site, self.token)
        headers = {
            'User-Agent': 'curl/7.12.1',
            'Host': 'data.zz.baidu.com',
            'Content-Type': 'text/plain',
            'Content-Length': '83',
        }
        response = requests.post(post_url, headers=headers, data=self.site)
        req = response.text
        if "success" in req:
            req_json = json.loads(req)
            if req_json["remain"] == 0:
                self.ttlog.log("普通收录-->查询剩余次数,今天普通收录推送任务已经完成,\n当天剩余的可推送url条数: " + req_json["remain"] + "条。")
            else:
                self.ttlog.log("普通收录-->查询剩余次数,推送成功：" + self.site + '\n当天剩余的可推送url条数: {}条'.format(req_json["remain"]))
            return req_json["remain"]
        else:
            return 0

    # 提交urls
    def api(self, url):
        post_url = "http://data.zz.baidu.com/urls?site={}&token={}".format(self.site, self.token)
        headers = {
            'User-Agent': 'curl/7.12.1',
            'Host': 'data.zz.baidu.com',
            'Content-Type': 'text/plain',
            'Content-Length': '83',
        }
        response = requests.post(post_url, headers=headers, data=url[0])
        req = response.text
        if "success" in req:
            req_json = json.loads(req)
            if req_json["remain"] == 0:
                self.ttlog.log("普通收录-->今天普通收录推送任务已经完成,当天剩余的可推送url条数: 0条。")
            else:
                # 是否修改列表，看是否加载列表
                tree_len = len(self.tree.get_children())
                if tree_len != 0:
                    print("普通收录-->修改列表")
                    self.tree.item(url[4], value=(url[0], "已提交", url[2], url[3]))

                # 修改数据库
                self.mydict[url[0]] = [url[0], "已提交", url[2], url[3], url[4]]
                self.ttlog.log("普通收录-->推送成功：" + url[0] + '\n当天剩余的可推送url条数: {}条'.format(req_json["remain"]))
        else:
            req_json = json.loads(req)
            self.ttlog.log(r"普通收录-->推送失败:" + req_json["message"] + "，当天可剩余推送数量为0条。")

        return None

    # 处理函数
    def main(self):
        # 获取未提交的urls
        urls = self.get_url()
        # 查询剩余次数
        num = self.get_remain()
        # 确定执行的urls
        post_urls = urls[:num]
        # 是否开始处理
        flag = tk.messagebox.askquestion("提交", "本地共有没推送的网页数 ：{} 条!\n"
                                               "当前剩余主动推送的次数 ：{} 条!\n"
                                               "选“是”开始提交，选“否”取消提交".format(len(urls), num))

        if flag == "yes":
            try:
                # 窗体置顶
                self.newroot.wm_attributes('-topmost', 1)
                cpu_num = multiprocessing.cpu_count()
                self.ttlog.log("CPU核心数：" + str(cpu_num))
                self.ttlog.log("开启线程池，能一定程度加速")
                pool = ThreadPool(cpu_num)
                results = pool.map(self.api, post_urls)
                pool.close()
                pool.join()
                self.ttlog.stop_log()
                self.ttlog.log("普通收录-->今日的推送任务完成！")
                self.content.config(text="普通收录-->今日的推送任务完成！")
            except Exception as e:
                self.ttlog.log('错误代码：{}'.format(e))
                self.ttlog.log("Error: unable to start thread")
        else:
            self.ttlog.log("你选择了否，没有推送网页链接")


class Wait_window(object):
    """重置窗体"""

    def __init__(self,tree,index):
        self.newroot = tk.Toplevel()
        self.newroot.title('处理中')
        self.newroot.iconbitmap("favicon.ico")
        self.newroot.wm_attributes('-topmost', 1)
        win_width = self.newroot.winfo_screenwidth()
        win_higth = self.newroot.winfo_screenheight()
        width_adjust = (win_width - 800) / 2
        higth_adjust = (win_higth - 250) / 2
        self.newroot.geometry("%dx%d+%d+%d" % (800, 250, width_adjust, higth_adjust))

        self.tree=tree
        self.index=index

        # 窗体日志
        self.ttlog = ttlog(master=self.newroot)
        self.ttlog.place(x=10, y=70, width=780, height=150)

        # 提示内容
        self.content = tk.Label(self.newroot, text="正在处理中,请不要中断操作，请耐心等待......")
        self.content.place(x=10, y=30, )
        self.content2 = tk.Label(self.newroot, text="")
        self.content2.place(x=50, y=60, )

        # 开启处理线程
        self.p = Thread(target=self.modify)
        self.p.setDaemon(True)
        self.p.start()

        self.newroot.protocol("WM_DELETE_WINDOW", self.close)

    # 处理函数
    def modify(self):
        mydict = SqliteDict('./my_db.sqlite', autocommit=True)
        if self.index==2:
            self.ttlog.log("快速收录重置-->开始")
        elif self.index==1:
            self.ttlog.log("普通收录重置-->开始")

        tree_len = len(self.tree.get_children())
        time.sleep(10)
        for key, value in sorted(mydict.iteritems()):
            if value[self.index]=="已提交":
                # 是否修改列表，看是否加载列表
                value[self.index] = "未提交"
                if tree_len != 0:
                    self.tree.item(value[4], value=value[:4])
                self.ttlog.log("重置状态："+key+"")
                # 修改数据库
                mydict[key] = value

        if self.index==2:
            self.ttlog.log("快速收录重置-->完成")
            self.content.config(text="快速收录重置-->完成")
        elif self.index==1:
            self.ttlog.log("普通收录重置-->完成")
            self.content.config(text="普通收录重置-->完成")
        self.ttlog.stop_log()

    def close(self):
        self.newroot.destroy()





if __name__ == "__main__":
    main = Main_window("百度站长提交工具V0.1 开源软件放心用 Github地址：https://github.com/Gaoyongxian666/baidu_submit", "favicon.ico")





# 自己打包
# pyinstaller -F -i f.ico C:\Users\Gao\PycharmProjects\百度提交工具\baidu.py
# 不带控制行
# pyinstaller -F -i favicon.ico C:\Users\Gao\PycharmProjects\百度提交工具\baidu.py -w
