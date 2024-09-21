from flask import Flask, request
from dym_form import form_view

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def form_route():
    return form_view()

if __name__ == '__main__':
    app.run(debug=True)
