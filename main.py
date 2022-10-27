import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from solveRecaptcha import solveRecaptcha
from fake_useragent import UserAgent
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
import requests
import json

d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = { 'driver':'ALL' }
options = Options()
ua = UserAgent(verify_ssl=False)
user_agent = ua.random
print(user_agent)
options.add_argument(f'user-agent={user_agent}')

with open("config.json", "r") as f:
    configFile = json.load(f)

webhook_url = configFile['webhook_url']
api_key = configFile['api_key']
site_key = configFile['site_key']
login_page = configFile['login_page']
lobby_page = configFile['lobby_page']
delay_mins = configFile['delay_mins']
email = configFile['user']['email']
password = configFile['user']['password']

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(login_page)

emailForm = driver.find_element(By.ID, 'login_email-input')
passwordForm = driver.find_element(By.ID, 'login_password-input')

emailForm.send_keys(email)
passwordForm.send_keys(password)

time.sleep(1)
passwordForm.send_keys(Keys.ENTER)

time.sleep(7)

if len(driver.find_elements(By.ID, 'daily-bonus__claim-btn')) > 0:
    claimButton = driver.find_element(By.ID, 'daily-bonus__claim-btn')
    claimButton.click()
    print('daily gift claimed')
else:
    print('no daily gift found')
if len(driver.find_elements(By.ID, 'offer__close')) > 0:
    closeButton = driver.find_element(By.ID, 'offer__close')
    closeButton.click()
    print('offer closed')
else:
    print('no offer found')

running = True

while running:
  try:
    driver.get(lobby_page)
    time.sleep(10)

    if len(driver.find_elements(By.ID, 'daily-bonus__claim-btn')) > 0:
        claimButton = driver.find_element(By.ID, 'daily-bonus__claim-btn')
        claimButton.click()
        print('daily gift claimed')
    else:
        print('no daily gift found')
    if len(driver.find_elements(By.ID, 'offer__close')) > 0:
        closeButton = driver.find_element(By.ID, 'offer__close')
        closeButton.click()
        print('offer closed')
    else:
        print('no offer found')

    time.sleep(2)
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight)"
    )

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'footer__postal-request-code'))
    )

    postalCodeFooter = driver.find_element(By.ID, 'footer__postal-request-code')
    postalCodeFooter.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'get-postal-request-code'))
    )
    postalCodeButton = driver.find_element(By.ID, 'get-postal-request-code')
    postalCodeButton.click()

    urlWithCaptcha = driver.current_url

    result = solveRecaptcha(
        site_key,
        urlWithCaptcha
    )

    code = result['code']

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'g-recaptcha-response'))
    )

    requrlforid = 'https://2captcha.com/in.php?json=1&key=' + api_key + '&method=userrecaptcha&googlekey=' + site_key + '&pageurl=' + urlWithCaptcha
    captchaIdReq = requests.get(requrlforid)
    time.sleep(7)
    jsonDataForId = json.loads(captchaIdReq.content)

    captchaId = jsonDataForId['request']
    print(captchaId + '\n')

    requrlforafterid = 'https://2captcha.com/res.php?json=1&key=' + api_key + '&action=get&id=' + captchaId
    time.sleep(30)
    tokenReq = requests.get(requrlforafterid)
    jsonDataForToken = json.loads(tokenReq.content)

    token = jsonDataForToken['request']
    print(token + '\n')

    time.sleep(1.5)

    captchaClient = driver.execute_script('''
    function findRecaptchaClients() {
    // eslint-disable-next-line camelcase
    if (typeof (___grecaptcha_cfg) !== 'undefined') {
        // eslint-disable-next-line camelcase, no-undef
        return Object.entries(___grecaptcha_cfg.clients).map(([cid, client]) => {
        const data = { id: cid, version: cid >= 10000 ? 'V3' : 'V2' };
        const objects = Object.entries(client).filter(([_, value]) => value && typeof value === 'object');

        objects.forEach(([toplevelKey, toplevel]) => {
            const found = Object.entries(toplevel).find(([_, value]) => (
            value && typeof value === 'object' && 'sitekey' in value && 'size' in value
            ));
        
            if (typeof toplevel === 'object' && toplevel instanceof HTMLElement && toplevel['tagName'] === 'DIV'){
                data.pageurl = toplevel.baseURI;
            }
            
            if (found) {
            const [sublevelKey, sublevel] = found;

            data.sitekey = sublevel.sitekey;
            const callbackKey = data.version === 'V2' ? 'callback' : 'promise-callback';
            const callback = sublevel[callbackKey];
            if (!callback) {
                data.callback = null;
                data.function = null;
            } else {
                data.function = callback;
                const keys = [cid, toplevelKey, sublevelKey, callbackKey].map((key) => `['${key}']`).join('');
                data.callback = `___grecaptcha_cfg.clients${keys}`;
            }
            }
        });
        return data;
        });
    }
    return [];
    }

    res = findRecaptchaClients();
    return res['0']['callback']
    ''')
    print("callback: " + captchaClient)

    driver.execute_script(
        captchaClient + "('" + token + "');"
    )

    time.sleep(3)

    file_name = "screenshot.png"
    current_path = os.getcwd()
    full_path = current_path + "\\" + file_name
    divclassoutcome = driver.find_element(By.CLASS_NAME, 'outcome')
    divunidchild = divclassoutcome.find_element(By.TAG_NAME, 'div')
    imagetoss = divunidchild.find_element(By.TAG_NAME, 'div')
    print(full_path)
    time.sleep(5)
    imagetoss.screenshot(full_path)

    webhook = DiscordWebhook(url=webhook_url)

    with open(full_path, "rb") as h:
        webhook.add_file(file=h.read(), filename=file_name)

    embed = DiscordEmbed(title='Postal Code', description='Code in image:', color='4800ff')
    embed.set_image(url='attachment://' + file_name)

    webhook.add_embed(embed)
    response = webhook.execute()

    backButton = driver.find_element(By.ID, 'return')
    backButton.click()

    #time.sleep(60 * delay_mins)
  except Exception as e:
    print("Continuing")
    print(str(e))
    continue
