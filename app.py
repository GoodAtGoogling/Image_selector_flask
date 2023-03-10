from flask import Flask, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_uploads import UploadSet, configure_uploads, IMAGES
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret_key"
app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'


photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

users = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create-account", methods=["POST"])
def create_account():
    username = request.form["username"]
    password = request.form["password"]

    if username in users:
        return "Username already taken"

    hashed_password = generate_password_hash(password)

    users[username] = hashed_password

    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            if check_password_hash(users[username], password):
                session["username"] = username
                return redirect("/welcome")
            else:
                return "Incorrect password"
        else:
            return "Incorrect username"

    return render_template("login.html")

@app.route("/welcome")
def welcome():
    if "username" in session:
        return render_template("welcome.html", username=session["username"])
    else:
        return redirect("/login")




@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "username" in session:
            file = request.files["photo"]
            if file and file.content_type.startswith('image'):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
                return redirect("/welcome")
            else:
                return "File type not allowed"
        else:
            return redirect("/login")
    else:
        return redirect("/welcome")


from PIL import Image

@app.route("/select-image", methods=["GET", "POST"])
def select_image():
    if request.method == "POST":
        if "username" in session:
            selected_image = request.form["image"]
            image_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], selected_image)
            if os.path.isfile(image_path):
                image = Image.open(image_path)
                image = image.resize((360, 360))
                image.save(image_path)
                return render_template("display-image.html", image=selected_image)
            else:
                return "Selected image not found"
        else:
            return redirect("/login")
    else:
        images = os.listdir(app.config['UPLOADED_PHOTOS_DEST'])
        return render_template("select-image.html", images=images)


    
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)


                                
