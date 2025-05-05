from flask import Flask, redirect, url_for
from admin import admin_bp

app = Flask(__name__)


app.register_blueprint(admin_bp)


@app.route('/')
def home():
    return redirect(url_for('admin.admin_panel'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
