# Dopia
一个web弱口令爆破器，基于Python，支持多线程，支持带请求头，支持中文。
在使用过程中，使用-h/--help命令查看帮助。
需求python版本：3以上。


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

一次执行必要的参数为-l/-L -p/-P --get/--post --success/--failure -o service。
