import json
import os
from flask import Flask, jsonify
import mysql.connector
import redis

app = Flask(__name__)

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    decode_responses=True
)


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'root'),
            database=os.getenv('MYSQL_DATABASE', 'testdb')
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


@app.route('/users/<int:user_id>/channels', methods=['GET'])
def get_user_channels(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
            SELECT c.*
            FROM channels c
                     JOIN channel_membership cm ON c.id = cm.channel_id
            WHERE cm.user_id = %s \
            """
    cursor.execute(query, (user_id,))
    channels = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({'channels': channels})


@app.route('/channels/<int:channel_id>/messages', methods=['GET'])
def get_channel_messages(channel_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT m.*, u.name AS sender_name
            FROM msgs m
                     JOIN users u ON m.sender_id = u.id
            WHERE m.channel_id = %s
            """
    cursor.execute(query, (channel_id,))
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'messages': messages})


from flask import request, jsonify


@app.route('/channels/<int:channel_id>/messages', methods=['POST'])
def send_message(channel_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    # e.g: {
    #   "text": "Hey!",
    #   "sender_id": 1
    # }

    # save message to db
    query = "INSERT INTO msgs (text, channel_id, sender_id) VALUES (%s, %s, %s)"
    cursor.execute(query, (data['text'], channel_id, data['sender_id']))

    sender_query = "SELECT name FROM users WHERE id = %s"
    cursor.execute(sender_query, (data['sender_id'],))
    sender = cursor.fetchone()
    sender_name = sender[0] if sender else None

    # publish the message to redis
    msg = json.dumps({
        'msg': data['text'],
        'sender_id': data['sender_id'],
        'sender_name': sender_name,
    })
    redis_client.publish(channel_id, msg)

    print(f"Message sent to channel {channel_id}: {data['text']}")
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'sent', 'message': json.loads(msg)}), 200


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
