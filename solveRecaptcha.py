import os
from twocaptcha import TwoCaptcha

def solveRecaptcha(sitekey, url):
    api_key = os.getenv('APIKEY_2CAPTCHA', '39c2e964d77f29ae843ed732da6f3652')
    solver = TwoCaptcha(api_key)

    try:
        result = solver.recaptcha(
            sitekey=sitekey,
            url=url)

    except Exception as e:
        print(e)

    else:
        return result