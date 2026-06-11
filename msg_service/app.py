import os
from flask import Flask, jsonify
import mysql.connector
import redis

app = Flask(__name__)

def init_redis_pub_sub():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)


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
    query = "SELECT * FROM msgs WHERE channel_id = %s"
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

    query = "INSERT INTO msgs (text, channel_id, sender_id) VALUES (%s, %s, %s)"
    cursor.execute(query, (data['text'], channel_id, data['sender_id']))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'sent'}), 200


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
