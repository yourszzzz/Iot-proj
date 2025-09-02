#!/usr/bin/env python3
"""
MINIMAL TEST: Basic Flask-SocketIO server to test WebSocket connection
"""

from flask import Flask, render_template
from flask_socketio import SocketIO
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Connection Test</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
</head>
<body>
    <h1>🧠 EEG System Connection Test</h1>
    <div id="status">Connecting...</div>
    <div id="log"></div>
    
    <script>
        const socket = io();
        const status = document.getElementById('status');
        const log = document.getElementById('log');
        
        socket.on('connect', function() {
            status.innerHTML = '✅ Connected to server!';
            status.style.color = 'green';
            addLog('Connected to WebSocket server');
        });
        
        socket.on('disconnect', function() {
            status.innerHTML = '❌ Disconnected from server';
            status.style.color = 'red';
            addLog('Disconnected from WebSocket server');
        });
        
        socket.on('test_message', function(data) {
            addLog('Received: ' + data.message);
        });
        
        function addLog(message) {
            const timestamp = new Date().toLocaleTimeString();
            log.innerHTML += '<div>' + timestamp + ' - ' + message + '</div>';
        }
    </script>
</body>
</html>
    '''

@socketio.on('connect')
def handle_connect():
    print('✅ Client connected!')
    socketio.emit('test_message', {'message': 'Hello from server!'})

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')

if __name__ == '__main__':
    print("🔧 Starting minimal test server on http://localhost:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)
