from flask import Flask, render_template,request,redirect, flash,session
from flask_sqlalchemy import SQLAlchemy
import hashlib
import re
import pickle
import random as rd
import smtplib

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
        if (len(p)<9):
            return "!! Password length is less then 9 !!"
        elif not re.search("[a-z]",p):
            return "!! Atleast single small character is required !!"
        elif not re.search("[0-9]",p):
            return "!! Atleast single digit is required !!"
        elif not re.search("[A-Z]",p):
            return "!! Atleast single capital character is required !!"
        elif not re.search("[$#@_]",p):
            return "!! Atleast one special character among $, #, @ or _ is required !!"
        elif re.search("\s",p):
            return "!! No voidspace allowed!!"
        else:
            return True

@app.route('/',methods=['GET','POST'])
@app.route('/login',methods=['GET','POST'])
def loginp_page():

    msg=None
    if 'email' in session:
        return render_template('index.html')
    
    if 'otp' in session:
        session.pop('otp')
        session.pop('otpemail')
        
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
            
        p = hashlib.md5(password.encode())

        lo=Users.query.filter_by(email=email).first()

        if lo is None:
            msg="You may have not signed up!!"
        elif lo.status=="Blocked":
                msg=lo.email+" is blocked by our admin!!"
        elif lo.password!=p.hexdigest():
            msg="Invalid Password entered"
        else:
            session['email']=email
            session['name']=lo.uname
            return redirect("/home")
        
        return render_template("login.html",msg=msg,m=request.form)
    return render_template("login.html")

@app.route('/signup',methods=['GET','POST'])
def signup_page():

    if 'email' in session:
        return render_template('index.html')
    
    msg=""
    if request.method=="POST":
        l=list()
        for i in request.form:
            l.append(request.form[i])

        s=strongpassword(l[2])
        c=Users.query.filter_by(email=l[1]).first()
        if c is not None:
            msg="!! Email already registered !!"
        
        elif l[2]!=l[3]:
            msg="!!New and Confirm password are not matched!!"

        elif s!=True:
            msg=s

        else:
            p = hashlib.md5(l[2].encode())
            log=Users(uname=l[0],email=l[1],password=p.hexdigest(),role="User",status="Unblocked")
            db.session.add(log)
            db.session.commit()
            flash("Successfully Sign Up","success")
            return redirect("/")
    
        return render_template("signup.html",msg=msg,m=request.form)
    
    return render_template("signup.html")

@app.route("/forget",methods=['GET','POST'])
def forget_password():
    if 'email' in session:
        return render_template('index.html')
    msg=""
    if 'otp' not in session:
        if request.method=="POST":             
            e=request.form['email']  

            lo=Users.query.filter_by(email=e).first()

            if lo is None:
                msg="!! No account with this email !!"
            else:      
                OTP=rd.randint(000000,999999)
                otp = str(OTP) + " is your OTP"
                msg= "Subject: One time password\n"+otp+"\n thanks"
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login("predictordisease@gmail.com", "mgsrthvsrtosljfr")
                s.sendmail('&&&&&&&&&&&&&&&&&',e,msg)    
                session['otp']=OTP
                session['otpemail']=e
                
                return redirect("/forget")
            
            return render_template("forget1.html",msg=msg,m=e)
        return render_template("forget1.html")

    if request.method=="POST":
        l=list()
        for i in request.form:
            l.append(request.form[i])    

        s=strongpassword(l[0])
        if l[0]!=l[1]:
            msg="!! New and Confirm password are not matched !!"
        elif s!=True:
            msg=s
        elif int(l[2])!=session['otp']:
            flash("!! Invalid OTP !!","warning")
            session.pop('otp')
            session.pop('otpemail')
            return redirect('/forget')
        else:
            p = hashlib.md5(l[0].encode())
            u=Users.query.filter_by(email=session['otpemail']).first()
            u.password=p.hexdigest()            
            db.session.add(u)
            db.session.commit()
            flash("Password change successfully","success")
            return redirect("/")

            
        return render_template("forget.html",msg=msg)

    return render_template("forget.html")

@app.route("/logout")
def logout_page():    
    if 'email' in session:
      session.pop('email')
      session.pop('name')
      flash("Logout Successfully","success")
    return redirect("/")


@app.route('/profile',methods=['GET','POST'])
def profile():
    if 'email' in session:        
        lo=Users.query.filter_by(email=session['email']).first()
        if request.method=="POST":
            l=list()
            for i in request.form:
                l.append(request.form[i])
            
            p = hashlib.md5(l[4].encode())

            if lo.password!=p.hexdigest():
                return render_template("profileupdate.html",lo=lo,msg="!! Invalid current password !!")
            f=0
            if lo.uname!=l[0]:
                lo.uname=l[0]
                f=1

            if lo.email!=l[1]:
                e=Users.query.filter_by(email=l[1]).first()
                if e is not None:
                    return render_template("profileupdate.html",lo=lo,msg="!! Email already registered !!")
                lo.email=l[1]
                f=1

            if l[2]!="":
                s=strongpassword(l[2])
                if l[2]!=l[3]:
                    return render_template("profileupdate.html",lo=lo,msg="!! New and confirm password not match !!")
                elif s!=True:
                    return render_template("profileupdate.html",lo=lo,msg=s)
                else:
                    p = hashlib.md5(l[2].encode())
                    lo.password=p.hexdigest()
                    f=1

            if f==1:
                db.session.add(lo)
                db.session.commit()                    
                flash("Your profile successfully updated","success")
            else:
                flash("Nothing is updated","success")

            return redirect('/logout')

        return render_template("profileupdate.html",lo=lo)
    return redirect("/")

@app.route('/home',methods=["GET","POST"])
def hello_world():
    if 'email' in session:
        return render_template("index.html")
    return redirect("/")

@app.route('/About')
def about():
    if 'email' in session:
        return render_template("about.html")
    return redirect("/")

@app.route('/BreastCancer',methods=['GET','POST'])
def Breast_Cancer():
    if 'email' not in session:
        return redirect("/")

    if request.method=='POST':
        l=list()
        rl=["\nWe have completed your breast cancer prediction and regret to inform you that our diagnosis result comes positive and you have breast cancer. We understand that this news may be difficult to hear, and we want to assure you that we are here to support you throughout the next steps of your journey.\n\nWe recommend that you schedule an appointment with your healthcare provider as soon as possible to discuss your results and develop a plan for further testing and treatment. Breast cancer is a serious disease, but with early detection and proper care, it is often treatable.\n\nThank you for trusting us with your healthcare needs.\n\nBest regards,\nDisease Predictor Team","\nWe have completed your breast cancer prediction and are pleased to inform you that our diagnosis result comes negative and you have no breast cancer. This is not a definitive diagnosis, but it is an encouraging sign that you are currently at a no risk for breast cancer.\n\nWe still recommend that you continue to schedule regular screenings and check-ups with your healthcare provider to monitor your breast health and detect any potential issues early. \n\nThank you for trusting us with your healthcare needs.\n\nBest regards,\nDisease Predictor Team"]
                
        for i in request.form:
            l.append(float(request.form[i]))

        pm=pickle.load(open('BreastCancer_LogisticRegression.pkl','rb'))
        re=pm.predict([l])
        r=["Dear "+session['name']+","]
        im=''
        msg="Subject: Breast Cancer Analysis\nDear "+session['name']+",\n"
      
        if re==1:
            im="positive"
            for i in rl[0].split('\n'):
                r.append(i)     
            msg+= ''.join(rl[0])
    
        else:    
            im="negative"
            for i in rl[1].split('\n'):
                r.append(i)
            msg+=''.join(rl[1])

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("predictordisease@gmail.com", "mgsrthvsrtosljfr")
        s.sendmail('&&&&&&&&&&&&&&&&&',session['email'],msg)   
            
        return render_template("breast out.html",l=im,r=r)

    return render_template("breast.html")

@app.route('/LungsCancer',methods=['GET','POST'])
def Lungs_Cancer():
    if 'email' not in session:
        return redirect("/")
    
    if request.method=='POST':
        l=list()
        rl=["\nWe have completed your lung cancer prediction and regret to inform you that our analysis indicates a high likelihood that you have lung cancer. We understand that this news may be difficult to hear, and we want to assure you that we are here to support you throughout the next steps of your journey.\n\nWe recommend that you schedule an appointment with your healthcare provider as soon as possible to discuss your results and develop a plan for further testing and treatment. Lung cancer is a serious disease, but with early detection and proper care, it is often treatable.\n\nThank you for trusting us with your healthcare needs.\n\nBest regards,\nDisease Predictor Team","\nWe have completed your lung cancer prediction and regret to inform you that our analysis indicates you have intermediate level of lung cancer. We understand that this news may be difficult to hear, and we want to assure you that we are here to support you throughout the next steps of your journey.\n\nWe recommend that you schedule an appointment with your healthcare provider as soon as possible to discuss your results and develop a plan for further testing and treatment. Lung cancer is a serious disease, but with early detection and proper care, it is often treatable.\n\nThank you for trusting us with your healthcare needs.\n\nBest regards,\nDisease Predictor Team","\nWe have completed your lung cancer prediction and are regret to inform you that our analysis indicates a low likelihood that you have lung cancer. This is not a definitive diagnosis, but it is an encouraging sign that you are currently at a low risk for lung cancer.\n\nWe still recommend that you continue to schedule regular screenings and check-ups with your healthcare provider to monitor your lung health and detect any potential issues early.\n\nThank you for trusting us with your healthcare needs.\n\nBest regards,\nDisease Predictor Team"]
        
        for i in request.form:
            l.append(float(request.form[i]))

        pm=pickle.load(open('lung_cancer_detection_Decision.pkl','rb'))
        re=pm.predict([l])
        r=["Dear "+session['name']+","]
        msg="Subject: Lung Cancer Analysis\nDear "+session['name']+",\n"
        
        if re[0]=='High':
            for i in rl[0].split('\n'):
                r.append(i)
            msg+= ''.join(rl[0])
        elif re[0]=="Medium":
            for i in rl[1].split('\n'):
                r.append(i)
            msg+= ''.join(rl[1])
        else:
            for i in rl[2].split('\n'):
                r.append(i)
            msg+= ''.join(rl[2])
        
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("predictordisease@gmail.com", "mgsrthvsrtosljfr")
        s.sendmail('&&&&&&&&&&&&&&&&&',session['email'],msg)   
        
        return render_template("lung out.html",l=re[0],r=r)

    return render_template("lung.html")

@app.route('/Heart',methods=['GET','POST'])
def Heart():
    if 'email' not in session:
        return redirect("/")
    
    if request.method=='POST':
        l=list()
        rl=["\nWe have completed your heart disease prediction and regret to inform you that our diagnosis result comes positive and you have heart disease. We understand that this news may be difficult to hear, and we want to assure you that we are here to support you throughout the next steps of your journey.\n\nWe recommend that you schedule an appointment with your healthcare provider as soon as possible to discuss your results and develop a plan for further testing and treatment. Heart disease is a serious disease, but with early detection and proper care, it is often treatable.\n\nThank you for trusting us with your healthcare needs.\n\nBest regards,\nDisease Predictor Team","\nWe have completed your heart disease prediction and are pleased to inform you that our diagnosis result comes negative and you have no heart disease. This is not a definitive diagnosis, but it is an encouraging sign that you are currently at a no risk for heart disease.\n\nWe still recommend that you continue to schedule regular screenings and check-ups with your healthcare provider to monitor your heart and detect any potential issues early.\n\nThank you for trusting us with your healthcare needs.\n\nBest regards,\nDisease Predictor Team"]

        for i in request.form:
            l.append(float(request.form[i]))

        pm=pickle.load(open('HeartDisease_Decision.pkl','rb'))
        re=pm.predict([l])
        r=["Dear "+session['name']+","]
        im=''
        msg="Subject: Heart Disease Analysis\nDear "+session['name']+",\n"
        if re==1:
            im="positive"
            for i in rl[0].split('\n'):
                r.append(i)       
            msg+= ''.join(rl[0])
    
        else:
            im="negative"
            for i in rl[1].split('\n'):
                r.append(i)    
            msg+= ''.join(rl[1])
        
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("predictordisease@gmail.com", "mgsrthvsrtosljfr")
        s.sendmail('&&&&&&&&&&&&&&&&&',session['email'],msg)       

        return render_template("heart out.html",l=im,r=r)

    return render_template("heart.html")

if __name__=="__main__":
    app.run(port=8080,debug=True)