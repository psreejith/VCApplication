from flask import *
# render_template, redirect, url_for, flash,request, session
import yaml
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import  create_engine  
from werkzeug.utils import secure_filename
from base64 import b64encode, b64decode
import io
import os
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField
from wtforms.validators import InputRequired, EqualTo, Length,DataRequired
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField 

app = Flask (__name__)

UPLOAD_FOLDER = 'static/profileImages/'
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif','bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


dbVal=yaml.load(open('db_val.yaml'))
app.config['MYSQL_HOST']=dbVal['ht']
app.config['MYSQL_USER']=dbVal['us']
app.config['MYSQL_PASSWORD']=dbVal['pw']
app.config['MYSQL_DB']=dbVal['db']
mysql = MySQL(app)
engine =  create_engine("mysql+pymysql://"+dbVal['us']+":"+dbVal['pw']+"@"+dbVal['ht']+"/"+dbVal['db']) 
db=scoped_session(sessionmaker(bind=engine))

    
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST': 
        username = request.form.get("username")
        password = request.form.get("password")

        if username is None:
            return render_template("login.html")
        else:
            usernamedata = db.execute("select username from tbl_users where username=:username",{"username":username}).fetchone()
            passworddata = db.execute("select password from tbl_users where username=:username",{"username":username}).fetchone()
            logindata = db.execute ("select firstlogin from tbl_users where username=:username",{"username":username}).fetchone()

            if usernamedata  is None:
                flash("No user","danger")
                return render_template('login.html')
            else:
                for password_data in passworddata:
                    if sha256_crypt.verify(password,password_data):
                        session["log"]= True    
                        session["username"] = username 
                        print("session set ->>>>>>>>>>>>>>>>>>>>>",session['username'])
                        #print(logindata[0])                      
                        if logindata[0] is  1:
                            print(logindata[0])
                            #flash("Logged In - Please update the Profile","success")
                            return render_template("profile.html",name=username)  #first login
                        else:
                            #flash("Logged In ","success")
                            return render_template("home.html",name=username)     #subsequent login
                    else:
                        flash("Incorrect Password","danger")
                        return render_template("login.html")
    return render_template("login.html")

@app.route("/", methods=['POST','GET'])
def index():
    return render_template("login.html")    

@app.route("/profile", methods=['POST','GET'])
def profile():    
    if 'username' in session:
        username = session['username'] 
         
        if request.method == "POST":
            if request.files:
                file = request.files["file"]
                firstname = request.form.get("firstname")
                lastname = request.form.get("lastname")
                email = request.form.get("email")
                phone=request.form.get("phone")
                print(file)
                filename = secure_filename(file.filename)
                print(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))                
                filename = "static/profileImages/"+ filename
                print(filename)
                with open(filename, "rb") as imageFile:
                    image = b64encode(imageFile.read())
                #image = b64encode(filename).decode("utf-8")
                #print("---------------------")
                #print(image)
                #print("-------------")
                #binaryImage = convertToBinaryData(filename)          # working
                #print(binaryImage)
                print(username)
                #select firstlogin from tbl_users where username=:username",{"username":username}
                db.execute("update tbl_users set firstname=:firstname, lastname=:lastname, email=:email, phone=:phone, datetime=:datetime, photo=:photo where username=:username",{"firstname":firstname,"lastname":lastname,"email":email,"phone":phone,"datetime":datetime.datetime.now(),"photo":image,"username":username})
                db.commit()
                #args = (firstname,lastname,email,phone,binaryImage,username)
                #print(query)
                #db.execute(query,args)
                #db.execute("update tbl_users set firstname=%s, lastname=%s, email=%s, phone=%s, photo=%s where username=%s",[{firstname,lastname,email,phone,binaryImage,username,}])
                #query="update tbl_users set firstname=%s, lastname=%s, email=%s, phone=%s, photo=%s where username=%s"
                #args = (firstname,lastname,email,phone,binaryImage,username)
                #db.execute(query,args)
                return render_template("profile.html",name=username) 
        else:
            records=db.execute("select * from tbl_users where username=:username",{"username":username})
            #records = db.fetchall()
            for row in records:               
                fname=row[1]
                lname=row[2]
                eml = row[3]
                phn = row[4]
                uname = row[5]
                image1 = row[8]
            img = b64decode(image1)
            filename = "static/profileimages/"+ uname+"_profileimage.jpg"
            print("profile file name",filename)
            with open(filename, 'wb') as f:
                f.write(img)
            profileimg = "static/profileimages/"+uname+"_profileimage.jpg"
            print(profileimg)
            return render_template("profile.html",name=username,fname=fname,lname=lname,eml=eml,phn=phn,profileimage=profileimg)  
    else:
        return render_template("login.html") 
 
@app.route('/home', methods=['POST','GET'])
def home():
    if 'username' in session:
        return render_template("home.html")  
    else:
        return render_template("login.html")    

@app.route('/schedulemeeting', methods=['POST','GET'])
def schedulemeeting():
    if request.method == 'POST':
        print("createinvitation value = " ,request.form.get('createinvitation'))
        if request.form.get('createinvitation') == "Checked" and request.form.get('meetingroomname') is not None:
            return render_template("schedulemeeting.html",meetingurl = "https://meet.cdit.org/TestRoom1?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb250ZXh0Ijp7InVzZXIiOnsiYXZhdGFyIjoiaHR0cHM6L2dyYXZhdGFyLmNvbS9hdmF0YXIvYWJjMTIzIiwibmFtZSI6IlJlbmppdGgiLCJlbWFpbCI6InJlbmppdGhAY2RpdC5vcmciLCJpZCI6ImFiY2Q6YTFiMmMzLWQ0ZTVmNi0wYWJjMS0yM2RlLWFiY2RlZjAxZmVkY2JhIn0sImdyb3VwIjoiYTEyMy0xMjMtNDU2LTc4OSJ9LCJhdWQiOiJDRElUTUVFVDc3NjRWWExWMDEiLCJpc3MiOiJDRElUTUVFVDc3NjRWWExWMDEiLCJzdWIiOiJtZWV0LmppdHNpIiwicm9vbSI6IlRlc3RSb29tMSIsImV4cCI6MTYxOTgyNzE5OX0.5k5nINoQSsGskj2oEzr6fKYeLLZ-uyzqqYlgHxr8OrU") 
     
    if 'username' in session:
        return render_template("schedulemeeting.html",meetingurl="")  
    else:
        return render_template("login.html")    
    
    
@app.route('/logout',methods=['POST','GET'])
def logout():
    if 'username' in session:
        session.pop('username',None) 
    return render_template("login.html")

class PasswordChangeForm(FlaskForm): 
    Username = StringField('Username',validators=[DataRequired(message='Username required')])
    OldPassword = PasswordField('OldPassword' ,validators=[InputRequired("Old Password Required")])
    NewPassword = PasswordField('NewPassword' ,validators=[InputRequired("New Password Required"),Length(min=5,max=10,message='New password must be 5 to 10 characters')])

@app.route('/passwordchange',methods=['GET','POST'])
def passwordchange():    
    form = PasswordChangeForm( )
    uname=session["username"]
    if form.validate_on_submit():
        return render_template('passwordchange.html',title='Password Change',form=form,name=uname)
    else:
        if request.method == 'POST':
            uname = request.form.get('Username')
            oldpwd = request.form.get('OldPassword')
            newpwd = request.form.get('NewPassword')  
            encryptnewpwd = sha256_crypt.encrypt(str(newpwd))
            print(encryptnewpwd)
            passworddata = db.execute ("select password from tbl_users where username=:username ",{"username":uname}).fetchone()
            for pass_data in  passworddata:
                if sha256_crypt.verify(oldpwd, pass_data):
                    db.execute("update tbl_users set password=:password where username=:username",{"password":encryptnewpwd, "username":uname})
                    db.commit()
                    flash("Password Changed successfully","success")    
                    return render_template('passwordchange.html',title='Password Change',form=form,name=uname)
                else:    
                    flash("Password not matching","danger")
                    return render_template('passwordchange.html',title='Password Change',form=form,name=uname)
    return render_template('passwordchange.html',title='Password Change',form=form,name=uname)

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

if __name__ == "__main__":
    app.secret_key  = "CDITSREe"
    app.run(debug=True)
    