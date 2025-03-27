from flask import Flask, render_template, request, jsonify
import json
import os
import ssl

app = Flask(__name__)

# Load valid names
with open('static/names.txt', 'r') as f:
    valid_names = [line.strip() for line in f]

# Load sign-in database
if os.path.exists('database.json'):
    with open('database.json') as f:
        sign_in_database = json.load(f)
else:
    sign_in_database = {}

@app.route('/')
def home():
    return render_template('late_signin.html')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/names')
def names():
    return jsonify(valid_names)

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    sign_in_database[data['uniqueID']] = data
    with open('database.json', 'w') as f:
        json.dump(sign_in_database, f)
    return jsonify({'message': 'Sign-in saved'})

@app.route('/get_entry/<uid>')
def get_entry(uid):
    entry = sign_in_database.get(uid)
    if entry:
        return jsonify(entry)
    else:
        return jsonify({'error': 'Not found'}), 404

@app.route('/rate/<uid>', methods=['POST'])
def rate(uid):
    data = request.json
    rating = data['rating']
    if uid in sign_in_database:
        sign_in_database[uid]['rating'] = rating
        with open('database.json', 'w') as f:
            json.dump(sign_in_database, f)
        return jsonify({'message': 'Rating saved'})
    else:
        return jsonify({'error': 'ID not found'}), 404

if __name__ == '__main__':
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain("server.crt", "server.key")  
    # Run app with HTTPS on port 5500
    app.run(host='0.0.0.0', port=5500, debug=True, ssl_context=context)
