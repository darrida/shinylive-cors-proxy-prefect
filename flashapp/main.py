import httpx
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

target_url = 'https://api.prefect.cloud/api'

@app.route('/prefect-proxy/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(subpath=''):
    try:
        # Make a request to localhost:11434 with the specified path
        target_url_with_path = f'{target_url}/{subpath}'
        print(target_url_with_path)
        response = requests.request(
            method=request.method,
            url=target_url_with_path,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=True
        )
        # Build the response
        resp = jsonify(response.json())
        resp.status_code = response.status_code

        # Set CORS headers
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = '*'
        print(resp.json)
        return resp

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)