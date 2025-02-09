from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Login')
def Login():
    return render_template('login.html')

@app.route('/Register')
def Register():
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)

