from flask import Flask, render_template, request, redirect, url_for
import socket
import json
import threading
from datetime import datetime
import os

app = Flask(__name__)

# Маршрутизація для index.html
@app.route('/')
def index():
    return render_template('index.html')

# Маршрутизація для message.html
@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        
        # Відправка даних на Socket сервер
        send_to_socket_server(username, message)
        return redirect(url_for('index'))
    return render_template('message.html')

# Обробка помилок 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

# Відправка даних на Socket сервер
def send_to_socket_server(username, message):
    data = json.dumps({'username': username, 'message': message}).encode('utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, ('127.0.0.1', 5000))
    sock.close()

# Функція для запуску Flask додатку
def run_flask():
    app.run(port=3000)

# Функція для запуску Socket сервера
def run_socket_server():
    if not os.path.exists('storage'):
        os.makedirs('storage')
    
    if not os.path.exists('storage/data.json'):
        with open('storage/data.json', 'w') as file:
            json.dump({}, file)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 5000))
    print("Socket сервер працює на порту 5000...")
    
    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode('utf-8'))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        with open('storage/data.json', 'r+') as file:
            try:
                json_data = json.load(file)
            except json.JSONDecodeError:
                json_data = {}
            json_data[timestamp] = message
            file.seek(0)
            json.dump(json_data, file, indent=4)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    socket_thread = threading.Thread(target=run_socket_server)
    
    flask_thread.start()
    socket_thread.start()
    
    flask_thread.join()
    socket_thread.join()