from flask import Flask,render_template,redirect,url_for,flash,request,session
import bcrypt
import string
import random
from flask_mysqldb import MySQL
from flask_mail import Mail,Message

from modules.login import Loginform
from modules.signup import Signupform
from modules.editprofile import EditProfileform
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods =['GET','POST'])
def login():
    form = Loginform()
    if request.method=='POST':
        email = form.email.data
        password = form.password.data
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM userdata WHERE email = %s", (email,))
        exist = cursor.fetchone()
        cursor.close()
        if exist and bcrypt.checkpw(password.encode('utf-8'),exist[5].encode('utf-8')):
            session['email'] = exist[4]
            return redirect(url_for('courses'))
        else:
            flash("Invalid credentials,Please re-check")
            return redirect(url_for('login'))
    return render_template('login.html', form = form)

def generate_password():
    char = string.ascii_letters + string.digits + string.punctuation
    new_password = ''.join(random.choice(char) for i in range(6)) 
    return new_password

@app.route('/forgot_password', methods = ['GET','POST'])
def forgot_password():
    if(request.method=='POST'):
        email = request.form['email']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM userdata WHERE email = %s", (email,))
        data = cursor.fetchone()
        if data:
            new_password = generate_password()
            hidden_password = bcrypt.hashpw(new_password.encode('utf-8'),bcrypt.gensalt())
            cursor.execute("UPDATE userdata SET password = %s WHERE email = %s", (hidden_password,email))
            mysql.connection.commit()
            msg = Message('Your New Password',recipients=[email])
            msg.body  = f'Your new Password is: {new_password}'
            mail.send(msg)
            flash('Your new password has successfully been sent to your Email ID')
        else:
            flash('The email you entered was not Registered.')
        cursor.close()
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route('/signup',methods =['GET','POST'])
def signup():
    form = Signupform()
    if form.validate_on_submit():
        firstname = form.firstname.data
        middlename = form.middlename.data
        lastname = form.lastname.data
        mobilenumber = form.mobilenumber.data
        email = form.email.data
        password = form.password.data
        if len(password)<=3:
            flash('Password length is too short')
            return redirect(url_for('signup'))
        hidden_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        
        # storing the data into database
        cursor = mysql.connection.cursor()
        #lets check if email is already taken
        cursor.execute("SELECT * FROM userdata WHERE email = %s", (email,))
        # single element tuple so we write (email,) and not (email)
        alr_exist = cursor.fetchone()
        if alr_exist:
            flash("The Email you entered is already used for some other account")
        else:
            cursor.execute("INSERT INTO userdata (f_name,m_name,l_name,mobile_no,email,password) VALUES (%s,%s,%s,%s,%s,%s)",(firstname,middlename,lastname,mobilenumber,email,hidden_password))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/register_courses', methods=['GET', 'POST'])
def register_courses():
    if 'email' not in session:
        flash('You have been logged out')
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    cursor.close()
    if request.method == 'POST':    
        courses_selected  = request.form.getlist('course_codes[]')
        email = session['email']
        if not courses_selected:
            flash('You havent selected any course, Please select atleast one.')
            return render_template('register_courses.html',courses = courses)
        cursor = mysql.connection.cursor()
        already_registered_courses = []
        for course_selected in courses_selected:
            cursor.execute("SELECT * FROM usercourses WHERE email = %s AND course_code = %s", (email,course_selected)) 
            exist = cursor.fetchone()
            if exist:
                already_registered_courses.append(course_selected)
        cursor.close()
        if already_registered_courses:
            flash(f'The following courses were already registered:- {",".join(already_registered_courses)}')
            return render_template('register_courses.html',courses = courses,courses_selected = courses_selected)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM usercourses WHERE email = %s", (email,))
        course_count = cursor.fetchone()[0]
        cursor.close()
        if len(courses_selected) + course_count>6:
            flash('You cannot register more than 6 courses')
            flash('Please go to the Registered Courses Page and unregister the unwanted courses if you have already registered some courses.')
            return render_template('register_courses.html',courses = courses,courses_selected = courses_selected)
        cursor = mysql.connection.cursor()
        for course_selected in courses_selected:
                cursor.execute("INSERT INTO usercourses (email,course_code) VALUES (%s,%s)", (email,course_selected))
        mysql.connection.commit()
        cursor.close()
        flash('Your courses have been successfully added')
        return redirect(url_for('courses'))
    return render_template('register_courses.html',courses = courses)

@app.route('/registered_courses')
def registered_courses():
    if 'email' not in session:
        flash('You have been logged out')
        return redirect(url_for('login'))
    email = session['email']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT u.course_code,c.course_name FROM usercourses AS u INNER JOIN courses AS c ON u.course_code = c.course_code WHERE email = %s", (email,))
    data = cursor.fetchall()
    return render_template('registered_courses.html', data = data)

@app.route('/unregister_course', methods = ['GET','POST'])
def unregister_course():
    if 'email' not in session:
        flash('You have been logged out')
        return redirect(url_for('login'))
    email = session['email']
    course_code = request.form.get('course_code')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT course_name FROM courses WHERE course_code = %s", (course_code,))
    course = cursor.fetchone()
    course_name = course[0]
    cursor.execute("DELETE FROM usercourses WHERE email = %s AND course_code = %s", (email,course_code))
    mysql.connection.commit()
    cursor.close()
    flash(f'You have successfully unregistered from the course: {course_name}')
    return redirect(url_for('registered_courses'))
    
@app.route('/reference_books')
def reference_books():
    return render_template('reference_books.html')
    
@app.route('/edit_profile', methods = ['GET','POST'])
def edit_profile():
    if 'email' not in session:
        flash('You have been logged out')
        return redirect(url_for('login'))
    form = EditProfileform()
    email = session['email']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM userdata WHERE email = %s', (email,))
    info = cursor.fetchone()
    cursor.close()
    if request.method == 'GET':
        # initially I am storing current data of the user already present in database
        form.firstname.data = info[0]
        if info[1]:
            form.middlename.data = info[1]
        else:
            form.middlename.data = ""
        form.lastname.data = info[2]
        form.mobilenumber.data = info[3]
        form.email.data = info[4]
    if request.method == 'POST' and form.validate_on_submit():
        if form.firstname.data:
            firstname = form.firstname.data
        else:
            firstname = info[0]
        middlename = form.middlename.data
        if form.lastname.data:
            lastname = form.lastname.data
        else:
            lastname = info[2]
        if form.mobilenumber.data:
            mobilenumber = form.mobilenumber.data
        else:
            mobilenumber = info[3]
        password = form.oldpassword.data
        if form.newpassword.data:
            newpassword = form.newpassword.data
        else:
            newpassword = form.oldpassword.data
        hidden_newpassword = bcrypt.hashpw(newpassword.encode('utf-8'),bcrypt.gensalt()) 
            # checking if form is completely unchanged
        if (firstname == info[0] and middlename == info[1] and lastname == info[2] and
            mobilenumber == info[3] and newpassword == password):
            return redirect(url_for('edit_profile'))
        cursor = mysql.connection.cursor()
        if bcrypt.checkpw(password.encode('utf-8'),info[5].encode('utf-8')):
            # we edit info in database
            cursor.execute("""UPDATE userdata SET f_name = %s, m_name = %s, l_name = %s, mobile_no = %s, password = %s WHERE email = %s""",(firstname,middlename,lastname,mobilenumber,hidden_newpassword,email))
            cursor.connection.commit()
            cursor.close()
            flash('Your profile has been sucessfully updated!')
            return redirect(url_for('edit_profile'))
        else:
            flash('The password you entered was incorrect! Please re-check.')
            return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form = form)
        
@app.route('/delete_account')
def delete_account():
    if 'email' not in session:
        flash('You have been logged out!')
        return redirect(url_for('login'))        
    email = session['email']
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM userdata WHERE email = %s", (email,))
    cursor.connection.commit()
    cursor.close()
    flash('Your account has been sucessfully deleted')
    return redirect(url_for('signup'))
    
@app.route('/logout')
def logout():
    session.pop('email',None)
    flash('You have been logged out')
    return redirect(url_for('login'))

if __name__ =="__main__":
    app.run(debug=True)