import pymysql as Mysql

mydb = Mysql.connect(host="localhost", user="root", password="", database="pollweb")
mycursor = mydb.cursor()

# mycursor.execute("CREATE TABLE login(Id INT NOT NULL AUTO_INCREMENT,Username CHAR(20),EmailId Char(30),FullName Char(20),Password Char(20),PRIMARY KEY (Id))")

mycursor.execute("CREATE TABLE PollQuestion(Id INT NOT NULL AUTO_INCREMENT,Question CHAR(200),Option1 Char(200),Option2 Char(200),Option3 Char(200),Option4 Char(200),Answer Char(200),Username Char(20),PRIMARY KEY (Id))")

# mycursor.execute(
#     "CREATE TABLE PollAnswer(Id INT NOT NULL AUTO_INCREMENT,Admin CHAR(200),Answer Char(200),UserName Char(200),Question Char(200), VeriAnswer Char(200), PollDate Date,PRIMARY KEY (Id))"
# )
