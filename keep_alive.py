from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "sky Project!"

def run():
    # Render әдетте 8080 немесе 10000 порттарын қолданады
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Веб-серверді бөлек процесте іске қосады"""
    t = Thread(target=run)
    t.start()
