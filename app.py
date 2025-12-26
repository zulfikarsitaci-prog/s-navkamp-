from flask import Flask, render_template, jsonify, send_from_directory
import json
import os

app = Flask(__name__)

# Anasayfa: index.html'i yükler
@app.route('/')
def index():
    return render_template('index.html')

# JSON Verisi: LifeSim sorularını JS'e gönderir
@app.route('/lifesim_data.json')
def get_lifesim_data():
    try:
        # JSON dosyası projenin ana dizininde olmalı
        with open('lifesim_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Veri dosyası bulunamadı."}), 404

# Statik dosyalar (Gerekirse resim/css vs. için)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
