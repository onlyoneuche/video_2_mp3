import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_service import access
from storage import util


server = Flask(__name__)
server.config['MONGO_URI'] = "mongodb://host.minikube.internal:27017/videos"

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters(host="172.17.0.2"))
channel = connection.channel()


# routes

@server.route('/login', methods=['POST'])
def login():
    token, err = access.login(request)
    if not err:
        return token
    return err


@server.route('/upload', methods=['POST'])
def upload():
    claims, err = validate.token(request)
    if err:
        return "not authorized", 401

    claims = json.loads(claims)
    if claims["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            err = util.upload(f, fs, channel, claims)

            if err:
                return err

        return "success!", 200
    else:
        return "not authorized", 401


# @server.route("/download", method=["GET"])
# def download():
#     pass


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
