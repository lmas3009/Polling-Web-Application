from flask import *
import uuid
import pymysql as Mysql
import requests

from datetime import date
import httplib2
import urllib


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# mydb = Mysql.connect(host="localhost", user="root", password="", database="pollweb")
# mycursor = mydb.cursor()


_uuid = uuid.uuid1()


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
    response = requests.get(
        "https://polling-web-application.herokuapp.com/pollquestion_id/" + id
    )
    new_data = json.loads(response.content)
    print(new_data)
    response1 = requests.get(
        "https://polling-web-application.herokuapp.com/pollanswer/"
        + session["user"]
        + "/"
        + new_data[0]["_id"]
    )
    new_data1 = json.loads(response1.content)
    print(new_data1)
    correct = wrong = 0
    data = []
    newdata = []
    for i in new_data1:
        data.append(str(i["PollDate"]))

    data.append(str(0))
    _data = sorted(list(set(data)))

    for j in _data:
        count = 0
        for k in data:
            if j == k:
                count += 1
        newdata.append(count)

    for i in new_data1:
        if new_data[0]["Answer"] == "Any One":
            correct += 1
        else:
            if i["Answer"].lower() == new_data[0]["Answer"].lower():
                correct += 1
            else:
                wrong += 1

    return render_template(
        "Statistic.html",
        data=new_data1,
        correct=str(correct),
        wrong=str(wrong),
        labels=_data,
        new_data=newdata,
    )


@app.route("/home")
def home():
    try:
        response = requests.get(
            "https://polling-web-application.herokuapp.com/pollquestion/"
            + session["user"],
        )
        new_data = json.loads(response.content)
        data = []
        options = []
        res = []
        for i in new_data:
            items = items1 = []
            items.append(i["_id"])
            items.append(i["Question"])
            items.append(i["Username"])
            data.append(items)
            options.append(i)
    except:
        return redirect("/")
    # print(options)
    return render_template(
        "home.html", data=data, uname=session["user"], options=options
    )


@app.route("/verify_register", methods=["POST", "GET"])
def verify_register():
    if request.method == "POST":
        uname = request.form["username"]
        fullname = request.form["fullname"]
        email = request.form["emailid"]
        password = request.form["password"]

        response = requests.get(
            "https://polling-web-application.herokuapp.com/login",
        )
        data = json.loads(response.content)
        length = len(data)
        if length != 0:
            for i in range(len(data)):
                if (uname != data[i]["Username"] or uname == "") and (
                    email != data[i]["EmailId"] or email == ""
                ):
                    response = requests.post(
                        "https://polling-web-application.herokuapp.com/login_add",
                        json={
                            "Username": uname,
                            "EmailId": email,
                            "FullName": fullname,
                            "Password": password,
                        },
                    )
                    print("Status code: ", response.status_code)
                    session["user"] = uname
                else:
                    return "Name or Email is already Used"
        else:
            response = requests.post(
                "https://polling-web-application.herokuapp.com/login_add",
                json={
                    "Username": uname,
                    "EmailId": email,
                    "FullName": fullname,
                    "Password": password,
                },
            )
            print("Status code: ", response.status_code)
            session["user"] = uname

    return redirect("/home")


@app.route("/verify_login", methods=["POST", "GET"])
def verify_login():
    if request.method == "POST":
        uname = request.form["username"]
        password = request.form["password"]

        # print(uname, password)
        try:
            response1 = requests.get(
                "https://polling-web-application.herokuapp.com/login/"
                + uname
                + "/"
                + password
            )
            data = json.loads(response1.content)
            if data != []:
                session["user"] = uname
                return redirect("/home")
        except Exception as e:
            return render_template("login.html", error=e)
    return redirect("/login")


@app.route("/create_poll")
def create_poll():
    return render_template("Createpoll.html", uname=session["user"])


@app.route("/add_poll", methods=["GET", "POST"])
def add_poll():
    if request.method == "POST":
        question = request.form["question"]
        option1 = request.form["opt1"]
        option2 = request.form["opt2"]
        option3 = request.form["opt3"]
        option4 = request.form["opt4"]
        answer = request.form["ans"]
        print(question, option1, option2, option3, option4, answer)
        name = session["user"]

        # if option1 == "":
        #     option1 = "NULL"
        # if option2 == "":
        #     option2 = "NULL"
        # if option3 == "":
        #     option3 = "NULL"
        # if option4 == "":
        #     option4 = "NULL"

        # cmd = "INSERT INTO `pollquestion`(`Question`, `Option1`, `Option2`, `Option3`, `Option4`, `Answer`, `Username`) VALUES(%s,%s,%s,%s,%s,%s,%s)"
        # val = (question, option1, option2, option3, option4, answer, session["user"])

        try:
            response = requests.post(
                "https://polling-web-application.herokuapp.com/pollquestion_add",
                json={
                    "Question": question,
                    "Option1": option1,
                    "Option2": option2,
                    "Option3": option3,
                    "Option4": option4,
                    "Answer": answer,
                    "Username": name,
                },
            )
            print("Status code: ", response.status_code)

        except Exception as e:
            return render_template("Createpoll.html", error=e)

    return redirect("/home")


@app.route("/viewpoll/<id>/<uname>")
def viewpoll(id, uname):

    response = requests.get(
        "https://polling-web-application.herokuapp.com/pollquestion/"
        + session["user"]
        + "/"
        + id,
    )
    new_data = json.loads(response.content)
    data = []
    print(new_data)
    votecount = 0
    for i in new_data:
        for j in i:
            data.append(i[j])
    try:

        response1 = requests.get(
            "https://polling-web-application.herokuapp.com/pollanswer/"
            + new_data[0]["_id"],
        )
        new_data1 = json.loads(response1.content)
        votecount = 0

        if new_data1:
            votecount = len(new_data1)

    except Exception as e:
        return str(e)
    return render_template(
        "Viewpoll.html", data=data, votecount=votecount, id=id, uname=uname, uuid=_uuid
    )


@app.route("/updatePoll/<id>", methods=["POST"])
def updatePoll(id):
    if request.method == "POST":
        opt1 = request.form["opt1"]
        opt2 = request.form["opt2"]
        opt3 = request.form["opt3"]
        opt4 = request.form["opt4"]
        ans = request.form["ans"]
        # print(opt1,opt2,opt3,opt4,ans)

        # cmd1 = "SELECT `question`, `username` FROM `pollquestion` WHERE `id`=%s"
        # val1 = (id)
        # mycursor.execute(cmd1,val1)
        # res1 = mycursor.fetchall()
        response = requests.get(
            "https://polling-web-application.herokuapp.com/pollquestion_update/"
            + opt1
            + "/"
            + opt2
            + "/"
            + opt3
            + "/"
            + opt4
            + "/"
            + ans
            + "/"
            + id,
        )
        # cmd = "UPDATE `pollquestion` SET `Option1` = %s,`Option2` = %s,`Option3` = %s,`Option4` = %s,`Answer` = %s WHERE `pollquestion`.`Id` = %s;"
        # val = (opt1, opt2, opt3, opt4, ans, id)
        # res = mycursor.execute(cmd, val)
        # mydb.commit()
        # print(res)
        if response:
            return redirect("/home")
    return ""


@app.route("/delete/<id>/<uuid>/<uname>")
def delete(id, uuid, uname):
    flag = False
    if str(uuid) == str(_uuid):
        if uname == session["user"]:
            response = requests.get(
                "https://polling-web-application.herokuapp.com/pollquestion_id/" + id,
            )
            new_data = json.loads(response.content)

            response1 = requests.get(
                "https://polling-web-application.herokuapp.com/pollquestion_delete/"
                + id
            )
            print(response1.status_code)
            response2 = requests.get(
                "https://polling-web-application.herokuapp.com/pollanswer_delete/"
                + new_data[0]["Question"]
            )
            print(response2.status_code)
            flag = True
    if flag == True:
        return redirect("/home")
    else:
        return render_template("404.html")

    return ""


@app.route("/Generatinglink/<id>")
def Generatinglink(id):
    _uuid = uuid.uuid1()
    return redirect(url_for("shareablelink", id=id, _uuid=_uuid, uname=session["user"]))


@app.route("/shareablelink/<id>/<uname>/<_uuid>")
def shareablelink(id, _uuid, uname):
    try:
        url = "shareablelink/" + id + "/" + uname + "/" + _uuid

        response = requests.get(
            "https://polling-web-application.herokuapp.com/pollquestion/"
            + uname
            + "/"
            + id,
        )
        new_data = json.loads(response.content)
        data = []

        response1 = requests.get(
            "https://polling-web-application.herokuapp.com/pollanswer/"
            + new_data[0]["_id"],
        )
        new_data1 = json.loads(response1.content)

        votecount = 0

        if new_data1:
            votecount = len(new_data1)

        for i in new_data:
            data.append(i["_id"])
            data.append(i["Question"])
            data.append(i["Option1"])
            data.append(i["Option2"])
            data.append(i["Option3"])
            data.append(i["Option4"])
            data.append(i["Username"])
    except Exception as e:
        print(e)

    return render_template(
        "shareable.html",
        data=data,
        len=len(data),
        votecount=votecount,
        url=url,
        uname=uname,
    )


@app.route("/answer/<uname>/<id>", methods=["POST"])
def answer(uname, id):
    if request.method == "POST":
        value = request.form["pollq"]
        name = request.form["name"]

        response1 = requests.get(
            "https://polling-web-application.herokuapp.com/pollquestion_id/" + id,
        )
        print(response1.status_code)
        new_data = json.loads(response1.content)

        # today = date(2021,3,23)
        # today = date.today()
        print(new_data)
        correct = "False"
        if new_data[0]["Answer"] == value:
            correct = "True"
        if new_data[0]["Answer"] == "Any One":
            correct = "True"

        try:
            response = requests.post(
                "https://polling-web-application.herokuapp.com/pollanswer_add",
                json={
                    "Admin": uname,
                    "Answer": value,
                    "Username": name,
                    "Question": new_data[0]["Question"],
                    "VeriAnswer": correct,
                    "QuestionId": new_data[0]["_id"],
                },
            )
            print("Status code: ", response.status_code)
            return "Thanks For Polling The Question! 😍"
        except Exception as e:
            return render_template("shareable.html", error=e, len=0, data=[])
    return ""


@app.route("/Dashboard")
def Dashboard():
    response1 = requests.get(
        "https://polling-web-application.herokuapp.com/pollanswer_admin/"
        + session["user"],
    )
    new_data = json.loads(response1.content)
    data = []
    correct = wrong = 0
    for i in new_data:
        if i["VeriAnswer"] == "True":
            correct += 1
        else:
            wrong += 1
        data.append(i)

    labels = ["Correct", "Wrong"]

    values = [correct, wrong]

    return render_template(
        "Dashboard.html",
        data=data,
        correct=correct,
        wrong=wrong,
        max=50,
        labels=labels,
        values=values,
    )


if __name__ == "__main__":
    app.run()
