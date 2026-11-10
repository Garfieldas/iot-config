from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    context: dict = {
        "title": "8G Dashboard",
    }
    return render_template('pages/home.html', **context)

if __name__ == '__main__':
    app.run(debug=True)