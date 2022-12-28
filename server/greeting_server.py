import os
import re
import json
from datetime import datetime

import openai
from flask import Flask, request
from flask import send_file
from flask_cors import CORS, cross_origin

LOGS_SECRET = os.environ.get('LOGS_SECRET', 'anotherone')
TUNED_MODEL_ID = os.environ.get('TUNED_MODEL_ID', 'davinci:ft-personal-2022-12-28-20-27-55')
QUERY_LOG_PATH = os.environ.get('QUERY_LOG_PATH', '/tmp/newyear.queries.jsonl')

START = "Дополни это поздравление с новым годом неожиданным прикольным добрым и позитивным образом: "
DELIMITER = "\nДополнение:"
STOP = "\n###\n"


# get completion for a prompt
def get_completion(prompt: str):
    response = openai.Completion.create(
        model=TUNED_MODEL_ID,
        prompt=START + prompt + DELIMITER,
        max_tokens=1500,
        temperature=0.7,
        stop=STOP,
    )
    return response


class CongratRequest:
    prompt: str

    def __init__(self, prompt: str):
        self.prompt = prompt


def validate_form(form: dict[str, str]) -> CongratRequest:
    prompt = form.get('prompt')
    if not prompt:
        raise ValueError("invalid_prompt")
    if len(prompt) < 10:
        raise ValueError("prompt_too_short")
    return CongratRequest(prompt=prompt)


# start webserver to handle requests
def main(query_log_fh):
    app = Flask(__name__)
    cors = CORS(app, resources={r"*": {"origins": "*"}})

    @app.route('/submit-congrat', methods=['POST'])
    @cross_origin()
    def greeting():
        if 'test' in request.form and request.form['test'] == 'test':
            return "ok", 200
        try:
            valid_req = validate_form(request.form)
        except ValueError as e:
            return {'error': str(e)}, 400

        try:
            response = get_completion(valid_req.prompt)
            query_log_fh.write(json.dumps({'timestamp': datetime.now().isoformat(), 'prompt': valid_req.prompt, 'choices': response['choices']}))
            query_log_fh.write("\n")
            query_log_fh.flush()
            return response['choices']
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/get-logs', methods=['GET'])
    def get_log():
        if request.args.get('secret') != LOGS_SECRET:
            return {'error': 'bad_secret'}, 401
        try:
            return send_file(QUERY_LOG_PATH)
        except Exception as e:
            return {'error': str(e)}, 500



    app.run(host='0.0.0.0', port=5000)

# CURL command to test the server:
# curl -X POST -F 'prompt=С Новым Годом!' http://localhost:5000/submit-congrat


if __name__ == "__main__":
    with open(QUERY_LOG_PATH, 'a') as query_log_fh:
        main(query_log_fh)
