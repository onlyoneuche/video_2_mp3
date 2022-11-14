import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL


server = Flask(__name__)
mysql = MySQL(server)

# config
server.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
server.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
server.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
server.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
server.config['MYSQL_PORT'] = os.environ.get('MYSQL_PORT')

# url paths

@server.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return "missing credentials", 401

    # check if user exists
    cur = mysql.connection.cursor()
    cur.execute("SELECT email, password FROM user WHERE email = %s", (auth.email,))

    # fetch one record and return result
    if cur.rowcount == 0:
        return "user not found", 401
    user_row = cur.fetchone()
    email = user_row[0]
    password = user_row[1]

    if auth.username != email or auth.password != password:
        return "invalid credentials", 401

    # generate jwt token
    return create_jwt(auth.username, os.environ.get('JWT_SECRET_KEY'), True)

@server.route('/validate', methods=['POST'])
def validate():
    encoded_token = request.headers.get('Authorization')
    if not encoded_token:
        return "missing token", 401

    token = encoded_token.split(' ')[1]

    try:
        decoded_token = jwt.decode(token, os.environ.get('JWT_SECRET_KEY'), algorithms=['HS256'])
        return decoded_token, 200
    except jwt.ExpiredSignatureError:
        return "expired token", 401
    except jwt.InvalidTokenError:
        return "invalid token", 401

def create_jwt(username, secret, is_admin):
    payload = {
        'email': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'admin': is_admin,
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, secret, algorithm='HS256').decode("utf-8")


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=5000, debug=True)