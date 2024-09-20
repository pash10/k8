from flask import Flask, request
from dym_form import Form

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def form_route():
    return Form()

if __name__ == '__main__':
    app.run(debug=True)
