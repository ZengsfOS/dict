import pymysql

def data_into_mysql(data):
	db = pymysql.connect(host = "localhost", user = "root", password = "123456",
database = data, charset = "utf8")
	cursor = db.cursor()
	f = open("./dict.txt")
	while True:
		try:
			for line in f:
				line = line.strip("\n")
				line1 = line[0:16].strip()
				line2 = line[16:].strip()
				cursor.execute("insert into words(word, interpret) values(%s, %s)", [line1,line2])
			else:
				break
		except:
			continue
	f.close()
	cursor.close()
	db.commit()
	db.close()
database = "dict"
data_into_mysql(database)

