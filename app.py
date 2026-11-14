from flask import Flask, request,render_template, redirect, url_for
import sqlite3
import joblib

app = Flask(__name__)

# Load models
tfidf = joblib.load("Models/tfidf_vectorizer.pkl")
model = joblib.load("Models/extension_voting.pkl")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/predict')
def prediction():
    return render_template("predict.html")

@app.route('/graphs')
def graphs():
    return render_template("graphs.html")

@app.route("/notebook")
def notebook():
    return render_template("Notebook.html")

@app.route('/logon')
def logon():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('signin.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        username = request.form.get('user','')
        name = request.form.get('name','')
        email = request.form.get('email','')
        number = request.form.get('mobile','')
        password = request.form.get('password','')
        con = sqlite3.connect('signup.db')
        cur = con.cursor()
        cur.execute("SELECT 1 FROM info WHERE user = ?", (username,))
        if cur.fetchone():
            con.close()
            return render_template("signup.html", message="Username already exists. Please choose another.")
        cur.execute("insert into `info` (`user`,`name`, `email`,`mobile`,`password`) VALUES (?, ?, ?, ?, ?)",(username,name,email,number,password))
        con.commit()
        con.close()
        return redirect(url_for('login'))

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html")
    else:
        mail1 = request.form.get('user','')
        password1 = request.form.get('password','')
        con = sqlite3.connect('signup.db')
        cur = con.cursor()
        cur.execute("select `user`, `password` from info where `user` = ? AND `password` = ?",(mail1,password1,))
        data = cur.fetchone()

        if data == None:
            return render_template("signin.html", message="Invalid username or password.")    

        elif mail1 == 'admin' and password1 == 'admin':
            return render_template("home.html")

        elif mail1 == str(data[0]) and password1 == str(data[1]):
            return render_template("home.html")
        else:
            return render_template("signin.html", message="Invalid username or password.")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/predict', methods=['POST'])
def predict():
    # Get input values from the form and convert to float
    text_input = request.form['text']
    final_input = tfidf.transform([text_input])
    
    # Predict using the model
    prediction = model.predict(final_input)[0]
    if prediction == 0:  # Not Spam
        context = {
            "result_label": "Not Spam",
            "title_message": "This Email is Safe!",
            "result_info": "Our AI model predicts that this email is NOT spam. You can safely open and read this message.",
            "recommendations": [
                "Always verify the sender if you are unsure.",
                "Be cautious with links and attachments, even in safe emails.",
                "Keep your email software up to date."
            ],
            "border_color": "#28a745",
            "header_bg_class": "bg-success",
            "icon_class": "bx-check-circle"
        }
        return render_template('result.html', **context)
    elif prediction == 1:  # Spam
        context = {
            "result_label": "Spam",
            "title_message": "Warning: Spam Detected!",
            "result_info": "Our AI model predicts that this email is SPAM. Please do not click on any links or download attachments from this message.",
            "recommendations": [
                "Do not respond to suspicious emails.",
                "Mark the email as spam in your email client.",
                "Delete the email if you are certain it is unwanted."
            ],
            "border_color": "#dc3545",
            "header_bg_class": "bg-danger",
            "icon_class": "bx-error"
        }
        return render_template('result.html', **context)

    
    

if __name__ == "__main__":
    app.run(debug=True)