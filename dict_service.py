'''
name:Zengsf
date:2018/9/28
email:zsf961006@163.com
modules:socket, os, time, signal, pymysql, sys
python 3.5.2
This is a dict project for AID
'''

from socket import *
import os
import time
import signal
import pymysql
import sys

#定义需要的全局变量,字典的文件路径以及服务器ip和端口号
DICT_TEXT = "./dict.txt"
HOST = "0.0.0.0"
PORT = 8000
ADDR = (HOST, PORT)


#子进程函数,主要就是接受客户端请求，并调用相对应的函数进行操作
def do_child(c, db):
	while True:
		data = c.recv(1024).decode()
		#c.getpeername()返回的是一个元组,(客户端IP，客户端的端口)
		print(c.getpeername(),":",data) 
		if (not data) or data[0] == "E":
			c.close()
			sys.exit(0)
		elif data[0] == "R":
			do_register(c, db, data)
		elif data[0] == "L":
			do_login(c, db, data)
		elif data[0] == "Q":
			do_query(c, db, data)
		elif data[0] == "H":
			do_hist(c, db, data)

#历史记录查询，就是通过名字，然后去数据库中进行查找进行了
def do_hist(c, db, data):
	print("历史记录")
	l = data.split()
	name = l[1]
	cursor = db.cursor()
	
	sql = "select * from hist where name='%s'" % name
	cursor.execute(sql)
	r = cursor.fetchall()    #这里返回的是一个元组，且是元组里面套元组
	if not r:
		c.send(b"FALL")
		return
	else:
		c.send(b"OK")
	
	for i in r:
		time.sleep(0.1)
		msg = "%s    %s    %s" % (i[1], i[2], i[3])
		c.send(msg.encode())
	time.sleep(0.1)			#有几处都是为了防止闭包，因此粘包
	c.send(b"##")

#查询有两种方法，一种是将数据放在文本中，另一种就是放在数据库中，这里用的是放在文本中，利用用户输出的单词，然后在去文本进行查找，只要是这种可以查询的，一定是有规律的，由于后面还有查询历史记录，因此，还有将查询出来的单词，姓名，时间都存到另一个数据库。
def do_query(c, db, data):
	print("查询操作")
	l = data.split()
	name = l[1]
	word = l[2]
	cursor = db.cursor()
	
	def insert_history():
		tm = time.ctime
		
		sql = "insert into hist(name,word,time) values('%s', '%s', '%s')" % (name,word,tm)
		try:
			cursor.execute(sql)
			db.commit()
		except:
			bd.rollback()

	#文本查询
	try:
		f = open(DICT_TEXT)   #全局变量文件路径
	except:
		c.send(b"FALL")	
		return
	
	#读取每一行数据且进行遍历
	for line in f:
		tmp = line.split()[0]
		if tmp > word:   #当光标到需要查找的后面去了之后，就退出查找
			c.send(b"FALL")
			f.close()
			return
		elif tmp == word:
			c.send(b"OK")
			time.sleep(0.1)
			c.send(line.encode())
			f.close()
			insert_history()	#插入到历史记录表中
			return
	e.send(b"FALL")			#当文本遍历完还没有得到结果是执行
	f.close()

#登录就是将用户输入的账号和密码与数据库中的进行比较，如果有，就可以登录
def do_login(c, db, data):
	print("登录操作")
	cursor = db.cursor()
	l = data.split()
	name = l[1]
	passwd = l[2]
	sql = "select * from user where name='%s' and passwd='%s'" % (name, passwd)
	cursor.execute(sql)
	result = cursor.fetchone()
	print(result)
	if result == None:
		c.send(b"FALL")
	else:
		print("%s登录成功" % c)
		c.send(b"OK")

#注册操作，客户端输入信息，服务器去信息表中进行查找，如果不存在，则进行注册,且将用户信息插入到数据库中，否则用户已存在,告诉客户端用户已存在。
def do_register(c, db, data):
	print("注册操作")
	l = data.split()
	name = l[1]
	passwd = l[2]
	cursor = db.cursor()
	sql = "select * from user where name='%s'" % name
	cursor.execute(sql)
	r = cursor.fetchone() #返回的是一个元组

	if r != None:
		c.send(b"EXISTS")
		return

	#用户不存在，将用户插入数据库
	sql = "insert into user(name, passwd) values('%s', '%s')" % (name, passwd)
	try:
		cursor.execute(sql)
		db.commit()
		c.send(b"OK")
	except:
		db.rollback()
		c.send(b"FALL")
	else:
		print("%s注册成功" % name)

	

#主要的流程控制
def main():
	#创建数据库连接
	db = pymysql.connect("localhost","root","123456","dict")

	#创建套接字
	s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	s.bind(ADDR)
	s.listen(5)
	
	#忽略子进程信号
	signal.signal(signal.SIGCHLD, signal.SIG_IGN)

	while True:
		try:
			c, addr = s.accept()
			print("Connect from", addr)
		except KeyboardInterrupt:
			s.close()
			sys.exit("服务器退出")
		except Exception as e:
			print(e)
			continue

		#创建子进程
		pid = os.fork()
		if pid ==0:			#子进程负责处理客户端的请求
			s.close()
			do_child(c, db)
			print("子进程准备处理请求")
		else:				#父进程就连接客户端
			c.close()
			continue

if __name__ == "__main__":
	main()
