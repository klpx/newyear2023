import os
import re

import openai
from flask import Flask, request
from flask_recaptcha import ReCaptcha

DISABLE_RECAPTCHA = os.environ.get('DISABLE_RECAPTCHA', False)
RECAPTCHA_SITE_KEY = os.environ['RECAPTCHA_SITE_KEY']
RECAPTCHA_SECRET_KEY = os.environ['RECAPTCHA_SECRET_KEY']
TUNED_MODEL_ID = os.environ['TUNED_MODEL_ID']

START = "Дополни это поздравление с новым годом черным позитивным юмором: "
DELIMITER = "\nДополнение:"
STOP = "\n###\n"


# get completion for a prompt
def get_completion(prompt: str):
    response = openai.Completion.create(
        model=TUNED_MODEL_ID,
        prompt=START + prompt + DELIMITER,
        max_tokens=500,
        temperature=0.7,
        stop=STOP,
    )
    return response


class CongratRequest:
    prompt: str
    email: str

    def __init__(self, prompt: str, email: str):
        self.prompt = prompt
        self.email = email


def validate_form(form: dict[str, str]) -> CongratRequest:
    prompt = form.get('prompt')
    email = form.get('email')
    # validate email with simple regexp
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("invalid_email")
    if not prompt:
        raise ValueError("invalid_prompt")
    if len(prompt) < 10:
        raise ValueError("prompt_too_short")
    return CongratRequest(prompt=prompt, email=email)


# start webserver to handle requests
def main():
    app = Flask(__name__)
    app.config['RECAPTCHA_SITE_KEY'] = RECAPTCHA_SITE_KEY
    app.config['RECAPTCHA_SECRET_KEY'] = RECAPTCHA_SECRET_KEY
    recaptcha = ReCaptcha(app)

    @app.route('/recaptcha-key', methods=['GET'])
    def recaptcha_key():
        return recaptcha.get_code()

    @app.route('/submit-congrat', methods=['POST'])
    def greeting():
        if 'test' in request.form and request.form['test'] == 'test':
            return "ok", 200
        if not (DISABLE_RECAPTCHA or recaptcha.verify()):
            return "Recaptcha verification failed", 400
        try:
            valid_req = validate_form(request.form)
        except ValueError as e:
            return str(e), 400

        response = get_completion(valid_req.prompt)
        return response['choices']

    app.run(host='0.0.0.0', port=5000)

# CURL command to test the server:
# curl -X POST -F 'prompt=С Новым Годом!' -F 'email=alex@arigativa.ru' http://localhost:5000/submit-congrat


if __name__ == "__main__":
    main()
