# coding: utf-8

from flask import Flask, render_template, redirect, url_for, session, logging, request, flash
from models import db, User, UserDetail, Comment, PasswordReset
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_restful import Resource, Api
from flask_mail import Mail, Message
import os
import jwt
import requests
import comparisons
import predictions
import special_values
import current_datetime
import prediction_by_dt

app = Flask(__name__)

api = Api(app)
api_uri = "http://127.0.0.1:5000"

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
photos = UploadSet('photos', IMAGES)

app.config['SECRET_KEY'] = "timutdashboard"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dashboard.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img/users'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'timutsoftware@gmail.com'
app.config['MAIL_PASSWORD'] = 'flaskdashboard'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

configure_uploads(app, photos)

mail = Mail(app)

class get_comparisons(Resource):
    def get(self):
        return {'data': comparisons.main()}

class get_predictions(Resource):
    def get(self):
        return {'data': predictions.main()}

class get_prediction_by_dt(Resource):
    def get(self, datetime):
        return {'data': prediction_by_dt.main(datetime)}

class get_special_values(Resource):
    def get(self):
        return {'data': special_values.main()}

class get_current_datetime(Resource):
    def get(self):
        return {'data': current_datetime.main()}

api.add_resource(get_comparisons, '/api/v1/get_comparisons')
api.add_resource(get_predictions, '/api/v1/get_predictions')
api.add_resource(get_special_values, '/api/v1/get_special_values')
api.add_resource(get_current_datetime, '/api/v1/get_current_datetime')
api.add_resource(get_prediction_by_dt, '/api/v1/get_prediction_by_dt/<string:datetime>')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file_ext(filename):
    return '.' + str(filename.rsplit('.', 1)[1].lower())

def current_dt():
    date = requests.get(api_uri + '/api/v1/get_current_datetime').json()
    return date["data"]

@app.route("/")
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        user_detail = UserDetail.query.filter_by(
            user_id=session['user_id']).first()
        comment = Comment.query.filter_by(
            user_id=session['user_id']).order_by(Comment.date.desc()).first()
        if comment is not None:
            last_comment = comment.date
        else:
            last_comment = ""
        stats = dict(last_login=user_detail.last_login_at,
                     last_logout=user_detail.last_logout_at,
                     last_comment=last_comment)
        return render_template("index.html", stats=stats)

@app.route("/sensorstatistics")
def sensor_statistics():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        return render_template("sensorstatistics.html")

@app.route("/updateprofile", methods=["POST"])
def update_profile():
    try:
        user_detail = UserDetail.query.filter_by(
            user_id=session['user_id']).first()
        user_detail.fullname = request.form['newfullname']
        newpic = request.files['newimage']
        if newpic and allowed_file(newpic.filename):
            filename = session['user_name'] + allowed_file_ext(newpic.filename)
            filename_uri = '../' + \
                app.config['UPLOADED_PHOTOS_DEST'] + '/' + str(filename)
            if user_detail.image == filename_uri:
                os.remove(os.path.join(
                    app.config['UPLOADED_PHOTOS_DEST'] + '/', filename))
            photos.save(request.files['newimage'], name=filename)
            if user_detail.image != filename_uri:
                user_detail.image = '../' + \
                    app.config['UPLOADED_PHOTOS_DEST'] + '/' + filename
        user_detail.description = request.form['newdescription']
        user_detail.updated_at = current_dt()
        db.session.commit()
        session['full_name'] = user_detail.fullname
        session['image_url'] = user_detail.image
        if session['lang'] == "tr":
            flash("Profiliniz güncellenmiştir!", "success")
        else:
            flash("Your profile has been updated!", "success")
        return redirect(request.referrer)
    except Exception as e:
        if session['lang'] == "tr":
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
        else:
            flash("A malfunction caused by the system has occurred!", "danger")
        return redirect(request.referrer)

@app.route('/deleteprofile', methods=["POST"])
def delete_profile():
    try:
        user = User.query.filter_by(id=session['user_id']).first()
        user_detail = UserDetail.query.filter_by(user_id=user.id).first()
        comment = Comment.query.filter_by(user_id=user.id).first()
        if comment is not None:
            Comment.query.filter_by(user_id=id).delete()
        db.session.delete(user_detail)
        db.session.delete(user)
        db.session.commit()
        session.clear()
        return redirect(request.referrer)
    except Exception as e:
        if session['lang'] == "tr":
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
        else:
            flash("A malfunction caused by the system has occurred!", "danger")
        return redirect(request.referrer)

@app.route('/removeimage', methods=["POST"])
def remove_image():
    try:
        user_detail = UserDetail.query.filter_by(
            user_id=session['user_id']).first()
        filename = session['user_name'] + allowed_file_ext(user_detail.image)
        os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
        user_detail.image = "../static/img/users/default-profile.png"
        session['image_url'] = user_detail.image
        db.session.commit()
        if session['lang'] == "tr":
            flash("Resminiz kaldırılmıştır!", "success")
        else:
            flash("Your picture has been removed!", "success")
        return redirect(request.referrer)
    except Exception as e:
        if session['lang'] == "tr":
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
        else:
            flash("A malfunction caused by the system has occurred!", "danger")
        return redirect(request.referrer)

@app.route("/profiledetails")
def profile_details():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        user = User.query.filter_by(id=session['user_id']).first()
        user_detail = UserDetail.query.filter_by(
            user_id=session['user_id']).first()
        return render_template("profiledetails.html", user=user, userdetail=user_detail)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user = ""
        try:
            user = User()
            user = user.check(
                username=request.form['username'], password=request.form['password'])
            if len(str(request.form['password'])) < 4 or len(str(request.form['password'])) > 20:
                flash("Şifre uzunluğu 4-20 arasında olmalıdır!", "danger")
            elif user:
                session['logged_in'] = True
                session['user_id'] = user.id
                session['user_name'] = user.username
                session['email'] = user.email
                user_detail = UserDetail.query.filter_by(user_id=session['user_id']).first()
                session['full_name'] = user_detail.fullname
                session['lang'] = user_detail.language
                session['image_url'] = user_detail.image
                session['last_login_at'] = current_dt()
                return redirect(url_for('home'))
            else:
                flash("Hatalı giriş! Lütfen tekrar deneyiniz.", "danger")
            return redirect(request.referrer)
        except Exception as e:
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
            return redirect(request.referrer)
    else:
        if session.get('logged_in'):
            return redirect(url_for('home'))
        else:
            return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    if session["logged_in"] == True:
        try:
            save_last_logout()
            session.clear()
        except Exception as e:
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
        return redirect(request.referrer)
    else:
        return redirect(request.referrer)

def save_last_logout():
    user_detail = UserDetail.query.filter_by(
        user_id=session['user_id']).first()
    user_detail.last_login_at = session['last_login_at']
    user_detail.last_logout_at = current_dt()
    db.session.commit()

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        check_username = User.query.filter_by(
            username=request.form['username']).first()
        check_email = User.query.filter_by(email=request.form['email']).first()
        if check_username is not None:
            flash("Hatalı kayıt olma işlemi! Farklı bir kullanıcı adı giriniz.", "danger")
            return redirect(request.referrer)
        elif check_email is not None:
            flash("Hatalı kayıt olma işlemi! Farklı bir e-posta giriniz.", "danger")
            return redirect(request.referrer)
        elif len(str(request.form['password'])) < 4 or len(str(request.form['password'])) > 20:
            flash(
                "Hatalı kayıt olma işlemi! Parola uzunluğu 4-20 arasında olmalıdır.", "danger")
            return redirect(request.referrer)
        else:
            try:
                new_user = User()
                new_user.save(
                    username=request.form['username'], email=request.form["email"], password=request.form['password'])
                db.session.add(new_user)
                db.session.commit()
                new_user_detail = UserDetail(fullname=request.form['fullname'], description="",
                                             image="../static/img/users/default-profile.png",
                                             language="tr", user_id=new_user.id, created_at=current_dt())
                db.session.add(new_user_detail)
                db.session.commit()
                flash("Başarılı kayıt! Şimdi giriş yapabiirsiniz.", "success")
                return redirect(url_for('login'))
            except Exception as e:
                flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
                return redirect(request.referrer)
    else:
        if session.get('logged_in'):
            return redirect(url_for('home'))
        else:
            return render_template("register.html")

@app.route("/forgotpassword", methods=["GET", "POST"])
def forgot_password():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user is not None:
                encoded = jwt.encode({"email": user.email, "time": current_dt(
                )}, app.config.get('SECRET_KEY'), algorithm="HS256")
                msg = Message(subject="Şifre Yenileme",
                              recipients=[user.email])
                msg.sender = app.config["MAIL_USERNAME"]
                msg.reply_to = app.config["MAIL_USERNAME"]
                uri = api_uri + '/passwordreset/' + str(encoded)
                msg.html = '<a href='+'"' + uri + '"'+'>Tıklayınız!</a>'
                mail.send(msg)
                flash(
                    "Şifre yenileme için e-posta adresinize mail gönderilmiştir!", "success")
                return redirect(request.referrer)
            else:
                flash(
                    "Böyle bir e-posta sistemimizde yoktur! Lütfen tekrar deneyiniz.", "danger")
                return redirect(request.referrer)
        except Exception as e:
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
            return redirect(request.referrer)
    else:
        if session.get('logged_in'):
            return redirect(url_for('home'))
        else:
            return render_template("forgotpassword.html")

@app.route("/passwordreset/<string:token>", methods=["GET", "POST"])
def password_reset(token):
    if request.method == 'POST':
        try:
            if request.form['newpassword'] == request.form['confirmpassword']:
                decoded = jwt.decode(token, app.config.get(
                    'SECRET_KEY'), algorithm="HS256")
                password_reset = PasswordReset.query.filter_by(
                    email=decoded["email"]).first()
                user = User.query.filter_by(email=decoded["email"]).first()
                if password_reset is not None:
                    password_reset.token = token
                    password_reset.email = decoded["email"]
                else:
                    new_password_reset = PasswordReset()
                    new_password_reset.token = token
                    new_password_reset.email = decoded["email"]
                    db.session.add(new_password_reset)
                user.password = User().reset_password(
                    request.form['newpassword'])
                db.session.commit()
                flash("Şifreniz yenilenmiştir! Şimdi giriş yapabilirsiniz.", "success")
                return redirect(url_for('login'))
            else:
                flash(
                    "Girdiğiniz parolalar eşleşmemiştir! Lütfen tekrar deneyiniz.", "danger")
                return redirect(request.referrer)
        except Exception as e:
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
            return redirect(request.referrer)
    else:
        if session.get('logged_in'):
            return redirect(url_for('home'))
        else:
            return render_template("passwordreset.html")

@app.route("/language/<string:lang>", methods=["POST"])
def language(lang):
    if not session.get('logged_in'):
        return redirect(request.referrer)
    else:
        try:
            user_detail = UserDetail.query.filter_by(
                user_id=session['user_id']).first()
            user_detail.language = lang
            db.session.commit()
            session['lang'] = lang
        except Exception as e:
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
        return redirect(request.referrer)

@app.route("/aboutus")
def about_us():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        return render_template("aboutus.html")

@app.route("/contactus", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        try:
            msg = Message(subject=request.form['subject'], recipients=[
                          app.config["MAIL_USERNAME"]])
            if session['lang'] == "tr":
                name = "Ad-Soyad"
            else:
                name = "Name"
            msg.sender = request.form['email']
            msg.reply_to = request.form['email']
            msg.html = name + ": " + \
                request.form['name'] + "<br><br>" + request.form['message']
            mail.send(msg)
            if session['lang'] == "tr":
                flash("Mesajınız gönderilmiştir!", "success")
            else:
                flash("Your message has been sended!", "success")
            return redirect(request.referrer)
        except:
            if session['lang'] == "tr":
                flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
            else:
                flash("A malfunction caused by the system has occurred!", "danger")
            return redirect(request.referrer)
    else:
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        else:
            return render_template("contactus.html")

@app.route("/temperaturepredictions")
def temp_predict():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        return render_template("temperaturepredictions.html")

@app.route("/comments/<int:page_num>")
def comments(page_num):
    if session.get('logged_in'):
        comments = Comment.query.filter_by(
            user_id=session['user_id']).order_by(
            Comment.date.desc()).paginate(per_page=3, page=page_num)
        if len(comments.items) == 0:
            status = False
            if session['lang'] == "tr":
                comments = "Henüz bir yorum yazmadınız."
            else:
                comments = "You have not yet commented."
        else:
            status = True
        return render_template("comments.html", comments=comments, status=status)
    else:
        return redirect(url_for('login'))

@app.route('/addcomment', methods=["POST"])
def add_comment():
    try:
        new_comment = Comment(
            title=request.form['title'], content=request.form["comment"], 
            date=current_dt(), user_id=session['user_id'])
        db.session.add(new_comment)
        db.session.commit()
        if session['lang'] == "tr":
            flash("Yorumunuz kaydedilmiştir!", "success")
        else:
            flash("Your comment has been saved!", "success")
        return redirect(request.referrer)
    except:
        if session['lang'] == "tr":
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
        else:
            flash("A malfunction caused by the system has occurred!", "danger")
        return redirect(request.referrer)

@app.route('/updatecomment/<string:id>', methods=["POST"])
def update_comment(id):
    try:
        comment = Comment.query.filter_by(id=id).first()
        comment.title = request.form['newtitle']
        comment.content = request.form['newcomment']
        comment.date = current_dt()
        db.session.commit()
        if session['lang'] == "tr":
            flash("Yorumunuz güncellenmiştir!", "success")
        else:
            flash("Your comment has been updated!", "success")
        return redirect(request.referrer)
    except Exception as e:
        if session['lang'] == "tr":
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
        else:
            flash("A malfunction caused by the system has occurred!", "danger")
        return redirect(request.referrer)

@app.route('/deletecomment/<string:id>', methods=["POST", "GET"])
def delete_comment(id):
    try:
        comment = Comment.query.filter_by(id=id).first()
        db.session.delete(comment)
        db.session.commit()
        if session['lang'] == "tr":
            flash("Yorumunuz silinmiştir!", "success")
        else:
            flash("Your comment has been deleted!", "success")
        return redirect(request.referrer)
    except:
        if session['lang'] == "tr":
            flash("Sistemden kaynaklanan bir arıza meydana geldi!", "danger")
        else:
            flash("A malfunction caused by the system has occurred!", "danger")
        return redirect(request.referrer)

if __name__ == "__main__":
    db.init_app(app)
    db.app = app
    db.create_all()
    app.run(debug=True, threaded=True)