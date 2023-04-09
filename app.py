from flask import Flask, render_template,request,redirect, flash,session
from flask_sqlalchemy import SQLAlchemy
import hashlib
import re
import pickle

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///disease.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)


class Users(db.Model):
    uname=db.Column(db.String(20), nullable=False)
    email=db.Column(db.String(50), primary_key=True)
    role=db.Column(db.String(10),nullable=False)
    status=db.Column(db.String(10),nullable=False)
    password=db.Column(db.String(20), nullable=False)

def strongpassword(p):
    while True:  
        if (len(p)<9):
            break
        elif not re.search("[a-z]",p):
            break
        elif not re.search("[0-9]",p):
            break
        elif not re.search("[A-Z]",p):
            break
        elif not re.search("[$#@]",p):
            break
        elif re.search("\s",p):
            break
        else:
            return True

    return False


@app.route('/',methods=['GET','POST'])
def loginp_page():
    return render_template("login.html")

@app.route('/signup',methods=['GET','POST'])
def signup_page():
    
    if 'email' in session:
        flash("You are already login","success")
        return render_template('index.html')


    if request.method=="POST":
        l=list()
        for i in request.form:
            print(i)
            l.append(request.form[i])
        print(l)

        c=Users.query.filter_by(email=l[1]).first()
        if c is not None:
            flash("Email already register")
            return redirect("/signup")
        
        elif l[2]!=l[3]:
            flash("New and Confirm password are not matched")
            return redirect("/signup")
        
        elif not strongpassword(l[2]):
            msg="Password is too Weak"

        else:
            p = hashlib.md5(l[2].encode())
            print(l)
            log=Users(uname=l[0],email=l[1],password=p.hexdigest(),role="User",status="Unblocked")
            db.session.add(log)
            db.session.commit()
            flash("Successfully Sign Up","success")
            return redirect("/")
        
    return render_template("signup.html")

@app.route("/forget",methods=['GET','POST'])
def forget_password():
    return render_template("forget.html")

@app.route("/logout")
def logout_page():
    return redirect("/")

@app.route('/home',methods=["GET","POST"])
def hello_world():
    return render_template("index.html")

@app.route('/About')
def about():
    return render_template("about.html")

@app.route('/BreastCancer',methods=['GET','POST'])
def Breast_Cancer():
    if request.method=='POST':
        l=list()
        for i in request.form:
            l.append(float(request.form[i]))

        pm=pickle.load(open('BreastCancer_LogisticRegression.pkl','rb'))
        re=pm.predict([l])
        r="You are diagnosis is negative"
        if re==1:
            r="You are diagnosis is positive"

        return render_template("breast out.html",l=r)

    return render_template("breast.html")

@app.route('/LungsCancer',methods=['GET','POST'])
def Lungs_Cancer():
    if request.method=='POST':
        l=list()
        for i in request.form:
            l.append(float(request.form[i]))

        pm=pickle.load(open('lung_cancer_detection_Decision.pkl','rb'))
        re=pm.predict([l])
        r="Lung Cancer is "+re[0]
        print(r[15:])

        return render_template("lung out.html",l=r)

    return render_template("lung.html")

@app.route('/Heart',methods=['GET','POST'])
def Heart():
    if request.method=='POST':
        l=list()
        for i in request.form:
            l.append(float(request.form[i]))

        pm=pickle.load(open('HeartDisease_Decision.pkl','rb'))
        re=pm.predict([l])
        r="You are diagnosis is negative"
        if re==1:
            r="You are diagnosis is positive"

        return render_template("heart out.html",l=r)

    return render_template("heart.html")

if __name__=="__main__":
    app.run(port=8080,debug=True)