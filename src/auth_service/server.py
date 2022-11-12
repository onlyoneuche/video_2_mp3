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


def create_jwt(username, secret, is_admin):
    payload = {
        'email': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'admin': is_admin,
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, secret, algorithm='HS256').decode("utf-8")


