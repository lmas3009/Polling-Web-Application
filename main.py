from flask import *
import uuid
import pymysql as Mysql
import matplotlib.pyplot as plt
import pyperclip
from datetime import date


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


mydb = Mysql.connect(host="localhost", user="root", password="", database="pollweb")
mycursor = mydb.cursor()


_uuid= uuid.uuid1()

@app.route("/")
def index():
    if "user" in session:
        return redirect("/home")
    else:
        print("Hello")

    return render_template("index.html")


@app.route("/register")
def register():
    if "user" in session:
        return redirect("/home")
    return render_template("register.html")


@app.route("/login")
def login():
    if "user" in session:
        return redirect("/home")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/Statistic/<uname>/<id>")
def Statistic(uname, id):
    mycursor.execute(
        "SELECT `Question`,`Answer` FROM `pollquestion` WHERE `Id` = %s", id
    )
    res = mycursor.fetchall()

    cmd1 = "SELECT * FROM `pollanswer` WHERE `Admin`=%s and `Question`=%s"
    val1 = (uname, res[0][0])

    mycursor.execute(cmd1, val1)
    correct = wrong = 0
    res1 = mycursor.fetchall()
    data = []
    new_data = []
    for i in res1:
        data.append(str(i[6]))

    data.append(str(0))
    _data = sorted(list(set(data)))

    for j in _data:
        count = 0
        for k in data:
            if (j == k):
                count += 1
        new_data.append(count)


    for i in res1:
        if res[0][1] == "Any One":
            correct += 1
        else:
            if i[2].lower() == res[0][1].lower():
                correct += 1
            else:
                wrong += 1

    return render_template(
        "Statistic.html", data=res1, correct=str(correct), wrong=str(wrong), labels = _data, new_data = new_data
    )


@app.route("/home")
def home():
    try:
        cmd = "SELECT * FROM pollquestion WHERE `username`=%s"
        val = session["user"]
        mycursor.execute(cmd, val)
        res = mycursor.fetchall()
        data = []
        options = []
        for i in res:
            items = items1 = []
            items.append(i[0])
            items.append(i[1])
            items.append(i[7])
            data.append(items)
            options.append(i)
    except:
        return redirect("/")
    print(options)
    return render_template("home.html", data=data, uname=session["user"],options = options)


@app.route("/verify_register", methods=["POST", "GET"])
def verify_register():
    if request.method == "POST":
        uname = request.form["username"]
        fullname = request.form["fullname"]
        email = request.form["emailid"]
        password = request.form["password"]

        mycursor.execute("SELECT * FROM login")
        data = mycursor.fetchall()
        length = len(data)
        if length != 0:
            for i in range(len(data)):
                if (uname != data[i][0] or uname == "") and (
                    email != data[i][1] or email == ""
                ):
                    cmd = "INSERT INTO `login`(`Username`, `EmailId`, `FullName`, `Password`) VALUES(%s,%s,%s,%s)"
                    val = (uname, email, fullname, password)
                    mycursor.execute(cmd, val)
                    session["user"] = uname
                    mydb.commit()
                else:
                    return "Name or Email is already Used"
        else:
            cmd = "INSERT INTO `login`(`Username`, `EmailId`, `FullName`, `Password`) VALUES(%s,%s,%s,%s)"
            val = (uname, email, fullname, password)
            mycursor.execute(cmd, val)
            session["user"] = uname
            mydb.commit()

    return redirect("/home")


@app.route("/verify_login", methods=["POST", "GET"])
def verify_login():
    if request.method == "POST":
        uname = request.form["username"]
        password = request.form["password"]
        cmd = "SELECT `fullname` from login where `username`=%s and `password`=%s"
        val = (uname, password)
        print(uname, password)
        try:
            mycursor.execute(cmd, val)
            res = mycursor.fetchall()
            if res:
                session["user"] = uname
                return redirect("/home")
        except Exception as e:
            return render_template("login.html", error=e)
    return redirect("/login")


@app.route("/create_poll")
def create_poll():
    return render_template("Createpoll.html",uname = session['user'])


@app.route("/add_poll", methods=["GET", "POST"])
def add_poll():
    if request.method == "POST":
        question = request.form["question"]
        option1 = request.form["opt1"]
        option2 = request.form["opt2"]
        option3 = request.form["opt3"]
        option4 = request.form["opt4"]
        answer = request.form["ans"]

        # if option1 == "":
        #     option1 = "NULL"
        # if option2 == "":
        #     option2 = "NULL"
        # if option3 == "":
        #     option3 = "NULL"
        # if option4 == "":
        #     option4 = "NULL"

        cmd = "INSERT INTO `pollquestion`(`Question`, `Option1`, `Option2`, `Option3`, `Option4`, `Answer`, `Username`) VALUES(%s,%s,%s,%s,%s,%s,%s)"
        val = (question, option1, option2, option3, option4, answer, session["user"])

        try:
            mycursor.execute(cmd, val)
            mydb.commit()
        except Exception as e:
            return render_template("Createpoll.html", error=e)

    return redirect("/home")


@app.route("/viewpoll/<id>/<uname>")
def viewpoll(id,uname):

    cmd = "SELECT * FROM `pollquestion` WHERE `Id`=%s and `username`=%s"
    val = (id, uname)
    data = []
    votecount = 0
    try:
        mycursor.execute(cmd, val)
        res = mycursor.fetchall()

        cmd1 = "SELECT * FROM `pollanswer` WHERE `question`=%s"
        val1 = (res[0][1])
        mycursor.execute(cmd1, val1)
        res1 = mycursor.fetchall()

        votecount = 0

        if (res1):
            votecount = len(res1)

        for i in res:
            for j in i:
                data.append(j)
    except:
        return render_template('404.html')


    return render_template("Viewpoll.html", data=data,votecount = votecount,id=id,uname=uname,uuid=_uuid)


@app.route("/updatePoll/<id>",methods=["POST"])
def updatePoll(id):
    if request.method == "POST":
        opt1 = request.form['opt1']
        opt2 = request.form['opt2']
        opt3 = request.form['opt3']
        opt4 = request.form['opt4']
        ans = request.form['ans']
        print(opt1,opt2,opt3,opt4,ans)

        # cmd1 = "SELECT `question`, `username` FROM `pollquestion` WHERE `id`=%s"
        # val1 = (id)
        # mycursor.execute(cmd1,val1)
        # res1 = mycursor.fetchall()




        cmd = "UPDATE `pollquestion` SET `Option1` = %s,`Option2` = %s,`Option3` = %s,`Option4` = %s,`Answer` = %s WHERE `pollquestion`.`Id` = %s;"
        val = (opt1,opt2,opt3,opt4,ans,id)
        res = mycursor.execute(cmd,val)
        mydb.commit()
        print(res)
        if(res):
            return redirect('/home')
    return ""

@app.route("/delete/<id>/<uuid>/<uname>")
def delete(id,uuid,uname):
    flag = False
    if(str(uuid)==str(_uuid)):
        if(uname == session['user']):
            mycursor.execute("SELECT `Question` FROM `pollquestion` WHERE `Id`=%s",id)
            res = mycursor.fetchall()

            cmd = "DELETE FROM `pollquestion` WHERE `Id`=%s"
            val = (id)
            mycursor.execute(cmd,val)
            mydb.commit()

            cmd1 = "DELETE FROM `pollanswer` WHERE `Question`=%s"
            val1 = (res[0])
            mycursor.execute(cmd1,val1)
            mydb.commit()
            flag = True
    if(flag==True):
        return redirect("/home")
    else:
        return render_template('404.html')

    return ""


@app.route("/Generatinglink/<id>")
def Generatinglink(id):
    _uuid = uuid.uuid1()
    return redirect(url_for("shareablelink", id=id, _uuid=_uuid, uname=session["user"]))


@app.route("/shareablelink/<id>/<uname>/<_uuid>")
def shareablelink(id, _uuid, uname):
    url = "shareablelink/"+id+"/"+uname+"/"+_uuid;
    cmd = "SELECT * FROM `pollquestion` WHERE `Id`=%s and `username`=%s"
    val = (id, uname)
    mycursor.execute(cmd, val)
    res = mycursor.fetchall()
    data = []

    cmd1 = "SELECT * FROM `pollanswer` WHERE `question`=%s"
    val1 = (res[0][1])
    mycursor.execute(cmd1,val1)
    res1 = mycursor.fetchall()

    votecount = 0

    if(res1):
        votecount = len(res1)


    for i in res:
        data.append(i[0])
        data.append(i[1])
        data.append(i[2])
        data.append(i[3])
        data.append(i[4])
        data.append(i[5])
        data.append(i[7])

    return render_template("shareable.html", data=data, len=len(data),votecount = votecount,url = url)


@app.route("/answer/<uname>/<question>", methods=["POST"])
def answer(uname, question):
    if request.method == "POST":
        value = request.form["pollq"]
        name = request.form["name"]

        cmd1 = "SELECT `Answer` FROM `pollquestion` WHERE `Question`=%s"
        val1 = (question)
        mycursor.execute(cmd1,val1)
        res = mycursor.fetchall()
        # today = date(2021,3,23)
        today = date.today()
        correct = "False"
        if(res[0][0]==value):
            correct = "True"
        if(res[0][0]=="Any One"):
            correct = "True"

        cmd = "INSERT INTO `pollanswer`(`Admin`, `Answer`, `UserName`, `Question`, `VeriAnswer`, `PollDate`) VALUES(%s,%s,%s,%s,%s,%s)"
        val = (uname, value, name, question, correct,today)

        try:
            mycursor.execute(cmd, val)
            mydb.commit()
            return "Thanks For Polling The Question! 😍"
        except Exception as e:
            return render_template("shareable.html", error=e,len = 0,data = [])
    return ""



@app.route("/Dashboard")
def Dashboard():
    cmd = "SELECT * FROM `pollanswer` WHERE `Admin`=%s"
    val = (session['user'])
    mycursor.execute(cmd,val)
    res = mycursor.fetchall()
    data = []
    correct = wrong=  0
    for i in res:
        if i[5]=='True':
            correct += 1
        else:
            wrong += 1
        data.append(i)
    plot = plt.plot(correct)
    print(plot)
    labels = [
        'Correct', 'Wrong'
    ]

    values = [
        correct, wrong
    ]

    return render_template('Dashboard.html',data = data,correct = correct, wrong = wrong, max=50, labels=labels, values=values)


if __name__ == "__main__":
    app.run(debug=True)