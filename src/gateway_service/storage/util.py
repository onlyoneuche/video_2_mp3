import json, pika


def upload(f, fs, channel, claims):
    try:
        fid = fs.put(f)
    except Exception:
        return "Internal Server Error", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": claims["username"]
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except:
        fs.delete(fid)
        return "Internal Server Error", 500