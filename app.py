from flask import Flask, request, jsonify
from functools import wraps
import jwt
import datetime
import random
import pytz
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'avi10-mobile-deploy-2025'

users = {"trader@avi10.com": generate_password_hash("secure123")}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth = request.headers.get('Authorization')
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ")[1]
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['email']
        except:
            return jsonify({'error': 'Token invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if email in users and check_password_hash(users[email], password):
        token = jwt.encode({'email': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/signal', methods=['GET'])
@token_required
def get_signal(current_user):
    direction = random.choice(['UP', 'DOWN'])
    multiplier = round(2.8 + random.random() * 1.5, 2)
    confidence = round(80 + random.random() * 15, 1)
    zim_tz = pytz.timezone('Africa/Harare')
    signal_time = datetime.datetime.now(zim_tz).strftime("%H:%M:%S")
    return jsonify({
        'multiplier': f"{multiplier}X",
        'confidence': confidence,
        'signal_time': signal_time,
        'direction': direction
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
