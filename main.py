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
    'cert'
}
cred = credentials.Certificate(cert)
url_link = 'link'
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






