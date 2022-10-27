import os
from twocaptcha import TwoCaptcha

with open("config.json", "r") as f:
    configFile = json.load(f)

api_key = configFile['api_key']

def solveRecaptcha(sitekey, url):
    api_key = os.getenv('APIKEY_2CAPTCHA', api_key)
    solver = TwoCaptcha(api_key)

    try:
        result = solver.recaptcha(
            sitekey=sitekey,
            url=url)

    except Exception as e:
        print(e)

    else:
        return result
