#!/usr/bin/python3
#coding=utf-8

from socket import *
import sys
import getpass

#查询单词，如果输入的是##，就退出查单词，否则输入的内容发送给服务器，等待服务器的相应做相对应的功能
def do_query(s, name):
	while True:
		word = input("请输入要查找的单词:")
		if word == "##":
			break
		msg = "Q "+ name + " "+ word
		s.send(msg.encode())
		data = s.recv(1024).decode()
		if data == "OK":
			data = s.recv(2048).decode()
			print(data)
		else:
			print("暂时还没有这单词")
		

#查询历史记录，发送数据给服务器，然后等待回应
def do_hist(s, name):
	msg = "H {}".format(name)
	s.send(msg.encode())
	data = s.recv(1024).decode()
	if data == "OK":
		while True:
			data = s.recv(1024).decode()
			if data == "##":      #接受到##就代表结束，服务器做了防止粘包处理。
				break
			print(data)
	else:
		print("没有历史记录")


#注册账号，通过套接字，将数据发送给服务器，然后接受服务器的反馈做相对应的动作
def do_register(s):
	while True:
		name = input("User:")
		passwd = getpass.getpass()		#python自带库，密码登入可以不然别人看到
		passwd1 = getpass.getpass("Again:")
		
		if (" " in name) or (" " in passwd):
			print("用户名和密码不许有空格")
			continue
		elif passwd != passwd1:
			print("两次密码不一致")
			continue

		msg = "R {} {}".format(name, passwd)
		#发送消息
		s.send(msg.encode())
		#等待回复
		data = s.recv(1024).decode()
		if data == "OK":	
			return 0
		elif data == "EXISTS":
			return 1
		else:
			return 2

#登录，将用户输入的账号和密码发送给服务器，然后做相对应的动作
def do_login(s):
	while True:
		name = input("User:")
		passwd = getpass.getpass()
		msg = "L {} {}".format(name, passwd)
		s.send(msg.encode())
		data = s.recv(1024).decode()
		if data == "OK":
			return name
		else:
			return 


#登录成功之后，进入二级界面，因此在二级界面选择相对应的功能
def login(s, name):
		while True:
			print("-----------查询界面-----------")
			print("--1.查询--2.历史记录--3.退出--")
			print("------------------------------")
			try:
				cmd = int(input("输入选项"))
			except Exception as e:
				print("命令错误")
				continue
	
			if cmd not in [1,2,3]:
				print("输入有误，请从新输入。")
				sys.stdin.flush()  #清楚标准缓存区输入
				continue
			elif cmd == 1:
				do_query(s, name)
			elif cmd == 2:
				do_hist(s, name)
			elif cmd == 3:
				return


#创建网络连接
def main():
	#sys.argv是在终端输入
	if len(sys.argv) < 3:
		print("argv is error")
		return
	HOST = sys.argv[1]
	PORT = int(sys.argv[2])
	s = socket()
	try:
		s.connect((HOST, PORT))
	except Exception as e:
		print(e)
		return

	#通过输入不同的命令，执行不同的事情。利用if判断。
	while True:
		print("------------Welcome-------------")
		print("----1.注册---2.登录---3.退出----")
		try:
			cmd = int(input("输入选项"))
		except Exception as e:
			print("命令错误")
			continue

		if cmd not in [1,2,3]:
			print("输入有误，请从新输入。")
			sys.stdin.flush()  #清楚标准缓存区输入
			continue
		elif cmd == 1:
			r = do_register(s)
			if r == 0:
				print("注册成功")
			elif r == 1:
				print("用户存在")
			else:
				print("注册失败")
		elif cmd == 2:
			name = do_login(s)		#如果登入成功，就进入第二界面
			if name:
				print("登录成功")
				login(s, name)
					
			
			else:
				print("用户名或密码不正确")			
				
		elif cmd == 3:
			s.send(b"E")
			sys.exit("谢谢使用")

if __name__ == "__main__":
	main()
