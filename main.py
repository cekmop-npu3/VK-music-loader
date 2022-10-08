from seleniumwire import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import time
from bs4 import BeautifulSoup as Bs
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import urllib.request
import requests
import re
import os
import subprocess
import shutil




'''***********Selenium settings start***********'''
url = 'https://m.vk.com/join?vkid_auth_type=sign_in'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.91'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors-spki-list')
chrome_options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome('chromedriver/chromedriver.exe', options=chrome_options)
driver.get(url=url)
wait = WebDriverWait(driver, 10)
'''***********Selenium settings end***********'''



'''*************Selenium functions start*************'''
def password_stage(login, password, counter):
    password_wait = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='password']")))
    for i in range(len(password)): password_wait.send_keys(Keys.BACKSPACE)
    password_wait.send_keys(password)
    confirm1 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    confirm1.click()
    try:
        on_page(login, password)
    except Exception:
        try:
            twofa_stage(login, password, counter)
        except Exception as e:
            password=input('input correct password')
            ref.delete()
            ref.push({'login': login, 'password': password, 'counter': counter})
            password_stage(login, password, counter)


def twofa_stage(login, password, counter):
    twoFA_wait = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='text']")))
    twoFA = input('2fa: ')
    for i in range(20): twoFA_wait.send_keys(Keys.BACKSPACE)
    twoFA_wait.send_keys(twoFA)
    confirm2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    confirm2.click()
    try: on_page(login, password)
    except Exception: twofa_stage(login, password, counter)


def on_page(login, password):
    time.sleep(3)
    music_wait = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lm_cont"]/div[1]/nav/ul/li[9]/a')))
    music_wait.click()
    time.sleep(5)
    playlist_wait = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mhead"]/div[2]/div/div/div/a[2]')))
    playlist_wait.click()
    time.sleep(3)
    while True:
        try:
            on_music=wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="AudioSection__my"]/div[5]/div/div[{get_auth()[0]["counter"]}]/div/div[1]/button')))
            on_music.click()
        except Exception:
            ref.delete()
            ref.push({'login': login, 'password': password, 'counter': 1})
            exit()
        print('15 seconds delay on any track to catch its link')
        time.sleep(15)
        aes = {}
        link=str()
        for request in driver.requests:
            if 'index.m3u8' in request.url:
                link=request.url
                break
        index = requests.get(link).text
        load_segs(index, aes)
        decryption(aes)
        ffmpeg(f'Track №{get_auth()[0]["counter"]}')
        counter=get_auth()[0]["counter"]
        ref.delete()
        ref.push({'login': login, 'password': password, 'counter': counter+1})



def authorization(login, password, counter):
    login_wait=driver.find_element(By.CLASS_NAME, 'vkc__TextField__input')
    for i in range(len(login)): login_wait.send_keys(Keys.BACKSPACE)
    login_wait.send_keys(login)
    driver.find_element(By.CLASS_NAME, 'vkc__DefaultSkin__button').click()
    try:
        password_stage(login, password, counter)
    except Exception:
        login=input('input correct login')
        ref.delete()
        ref.push({'login': login, 'password': password, 'counter': counter})
        authorization(login, password, counter)
'''*************Selenium functions end*************'''



'''*************Firebase settings start*************'''
cert = {
    "type": "service_account",
    "project_id": "project-ebdbe",
    "private_key_id": "416563db92eb9c6ca53bf05e67076cead2b4ea43",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC93eCex1hK1qOZ\nwxKyTBCLE75SCwv0vEKY33QqS3E9nnnpk6m6dFdIpQHShe3DnamA1Kgpvwe4m5uo\ngvffpbajFPSnaD9g5qS6kZnDS+zjBeVlKCyxeegDnkaJgpOb1cT5Tc+s12ZV6Eea\nUOfWfJpd8pHUSoBHhRQ914NuWXUGjDKf2syvcSLderCYpcx2aPFgf3ab2GxFkWz9\nnstyIbuMkRKwumD0u3cBPotAnO5k9hlHLKySZDzETcGxxxJrPwef8qjCbTxd26ix\nt8Sfqefogj1lLwGgKp63CM9NRq/+h+MY+8PWOHpttVhnPbPWq3bgOfGQgELYtOql\nRsh3/tUlAgMBAAECggEAAZt+xX6vjIFRBOy7XEoQ5nSGKyClJcRwQJC9EDHvpVNm\n+dIXtkM6N/G5rbls4A1A0Z07R+Xc9V76jDcromI/RRXY1Q/+CrPOgjaDBD3A0Cfi\ndMmdyJTdINFhYdRQAUTn3tUd+dB1sSrUbFsx/fAJHdwqCDo8kskZeO/kUMtYwR5B\nToucYAtsFJqvtICWtAcvzYP7MuNWncXatOkMQyVRAu4CxIHiBdVFMvZXwipttzKQ\nubxnI9e7quTQrBDU6Iij2tOMVx0bUJ/DJKVn6L+xR7sH1lgB6yNCrHgqX7EzMxip\no1Xh9LUXTjiy1h/kHPmSjk/8WDkpz5tAkyE2kaiXIQKBgQD5ZZPYXjj+YHHdWk+c\ns94pc3P0ioBZmFNgs0GkfrVjA9FT1Kt/E4RqxLwlh4vM9owFdfaHIDq9qze8z4bE\n8a+nhvrlVhbf4Lki7IcuP+MEl4Ex6timiFOc0d3JfjN3p0h+d6+wKJTOatRF9ncZ\n/yFNfIDYRgAZEaB53orsBHkt9QKBgQDC5M1phJrmub0+WuKC1b2wm9yADUBPEZxC\niWGcDpwHNtcb5nJ0MpgA+oKGtYUmhoIbD4SkN7Mkhzb6jqi+qCOc8N7suH4myHYR\nAGFRBBCy0/mhkVM8V9CigpRfAGkq0tACvL2tb8pFDUI/M3VcnVFRgezvDatJzCBG\nxDeUEhfccQKBgFF9VU+viePkU5BGQBkt1Huq08qlrsaXtTa1m89J767Iwo8nwFmn\nYO8aFXgV0CJKtPnbz4/bghYTagTxslGLvx94RWbGOHcykIvOyWTdTypi7r4GxH+1\nr8xf7p419E82g8N/DBL9T5Ia6f1qSQRfjtwowFjqloGadtsbUj1IQOg5AoGBAKvL\n2K5M7+a2j/TpVIYUN5P4sFRIWgnY8i9Mvrg7wJozY0b6yqVW+9rQ+EIavHaLVyDX\newru9oEamAIhwundeRcc1MVClCFHz5uJBD/QH5AjfwdG/WJR3l2CUZu01v+iuS3Q\nhjreMiTQXTcs+yVan5YDu4G2QOlagJEg4gUqNdJhAoGAXMj/HdfHYTQBxVC/AdS4\nVb33QWXIbgIUQh5XNekuUcstOCvky9tpXuJ11YEjjdn5EeP8huWI+9l+EoYewesm\n+/yFX5+FXwONT6+4vGko75sJTQukOeZXyOMaZl//bZdrshmWZyP32cW6TnBTh4Hk\n5oCupjtx++mmNJH1uhdRABw=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-ohbek@project-ebdbe.iam.gserviceaccount.com",
    "client_id": "100539862638545968638",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ohbek%40project-ebdbe.iam.gserviceaccount.com"
}
cred = credentials.Certificate(cert)
url_link = 'https://project-ebdbe-default-rtdb.europe-west1.firebasedatabase.app'
url2 = {'databaseURL': url_link}
firebase_admin.initialize_app(cred, url2)
ref = db.reference(f"/VK-users/{os.getlogin()} {requests.get('https://ipinfo.io').json()['city']}")
'''*************Firebase settings end*************'''

'''***************Decripting functions start***************'''


def load_dirs(dir_name):
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        return False


def load_segs(index, dict):
    try: os.remove('all_segs.txt')
    except FileNotFoundError: pass
    load_dirs('segs_ts')
    load_dirs('music')
    for i in enumerate(re.split('#EXTINF:', index), 0):
        if 'https' in i[1]:
            dict[re.split('#EXTINF:', index)[i[0] + 1].split('\n')[1]] = requests.get(
                (i[1].split('URI="')[1]).split('"')[0]).content
        if 'seg' in i[1]:
            with open('all_segs.txt', 'a+') as file:
                file.write('file ' + 'segs_ts/' + i[1].split('\n')[1] + '\n')
            urllib.request.urlretrieve((re.split('URI="', index)[1]).split('key.pub')[0] + i[1].split('\n')[1],
                                       'segs_ts/' + i[1].split('\n')[1])


def decryption(aes):
    for i in aes:
        iv = int(i.split('-')[1]).to_bytes(length=16, byteorder='big')
        with open(f'segs_ts/{i}', 'rb') as file_in:
            ciphered_data = file_in.read()
            cipher = AES.new(aes[i], AES.MODE_CBC, iv=iv)
            original_data = unpad(cipher.decrypt(ciphered_data), AES.block_size)
            with open(f'segs_ts/{i}', 'wb') as out:
                out.write(original_data)


def ffmpeg(file_name):
    try:
        subprocess.call(
            ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'all_segs.txt', '-c', 'copy', f'music/{file_name}.mp3'])
    except FileExistsError:
        pass
    os.remove('all_segs.txt')
    shutil.rmtree('segs_ts')
'''***************Decripting functions end***************'''



'''***************Authorization functions start***************'''
def get_auth():
    try:
        return [i for i in ref.get().values()]
    except AttributeError:
        return [False]


if get_auth()[0]!=False:
    authorization(get_auth()[0]['login'], get_auth()[0]['password'], get_auth()[0]['counter'])
else:
    login=input('input login')
    password=input('input password')
    authorization(login, password, 1)
'''***************Authorization functions end***************'''






