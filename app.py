# import Library
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS

import time
import urllib.request
import urllib.parse
import urllib.error
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

import sys
import logging
import datetime

# initiate object flask
app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# initiate object flask_restful
api = Api(app)

# initiate object flask_cors
CORS(app)

identitas = {}


class ContohResource(Resource):
    __url = 'https://ibank.klikbca.com/'

    def get(self):
        # response = {"message": "Hello World"}
        return "REST API BCA"

    def post(self):
        username = request.form["username"]
        password = request.form["password"]
        identitas["username"] = username
        identitas["password"] = password
        self.__username = username
        self.__password = password
        response = self.login()
        return response

    def login(self):
        opts = webdriver.ChromeOptions()
        # opts.headless = True
        opts.add_argument('--# headless')
        opts.add_argument('--#disable-gpu')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')

        # self.__driver = webdriver.Chrome(
        #    ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install(), options=opts)
        self.__driver = webdriver.Chrome(
            executable_path=r'/app/.chromedriver/bin/chromedriver', options=opts)

        self.__driver.wait = WebDriverWait(self.__driver, 3)

        try:
            self.__driver.get(self.__url)
            username = self.__driver.wait.until(
                EC.presence_of_element_located((By.ID, "user_id")))
            password = self.__driver.wait.until(
                EC.element_to_be_clickable((By.ID, "pswd")))
            login_bca = self.__driver.wait.until(
                EC.presence_of_element_located((By.NAME, "value(Submit)")))
            username.send_keys(self.__username)
            password.send_keys(self.__password)
            login_bca.send_keys(webdriver.common.keys.Keys.SPACE)

            try:
                self.__driver.switch_to.frame(
                    self.__driver.find_element_by_xpath("//frame[@name=\"header\"]"))
                self.__driver.switch_to.default_content()
                return self.cekSaldo()
            except:
                alert = self.__driver.switch_to.alert()
                # return alert.text
                # return {"message": "Login gagal 1"}
                return (jsonify({
                    'code': 400,
                    'success': 'false',
                    'message': 'balance check failed',
                    'data': {}
                }))
                alert.accept()

        except:
            # return {"message": "Login gagal 2"}
            return (jsonify({
                'code': 400,
                'success': 'false',
                'message': 'login failed',
                'data': {}
            }))

    def cekSaldo(self):
        try:
            self.__driver.switch_to.frame(
                self.__driver.find_element_by_xpath("//frame[@name=\"menu\"]"))
            mutasi = self.__driver.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[@href=\"account_information_menu.htm\"]")))
            mutasi.click()
            cek_saldo = self.__driver.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[@onclick=\"javascript:goToPage('balanceinquiry.do');return false;\"]")))
            cek_saldo.click()
            self.__driver.switch_to.default_content()
            self.__driver.switch_to.frame(
                self.__driver.find_element_by_xpath("//frame[@name=\"atm\"]"))
            saldo = self.__driver.find_element_by_xpath(
                "//table[3]/tbody//tr[2]//td[4]").text
            # print(("Saldo BCA saat ini adalah %s" % saldo))
            self.__driver.switch_to.default_content()
            self.logout()
            return (jsonify({
                'code': 200,
                'success': 'true',
                'message': 'data found',
                'data': {
                    'balance': '%s' % saldo,
                    'timestamp': '%s' % datetime.datetime.now()
                }
            }))
        except TimeoutException:
            # return {"message": "Session timeout. please login again"}
            return (jsonify({
                'code': 400,
                'success': 'false',
                'message': 'session timeout',
                'data': {}
            }))

    def logout(self):
        try:
            self.__driver.switch_to.frame(
                self.__driver.find_element_by_xpath("//frame[@name=\"header\"]"))
            logout = self.__driver.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[@onclick=\"javascript:goToPage('authentication.do?value(actions)=logout');return false;\"]")))
            logout.click()
            print("Anda berhasil logout")
        except TimeoutException:
            print("Session timeout. please login again")


# setup resource
api.add_resource(ContohResource, "/api", methods=["GET", "POST"])

if __name__ == "__main__":
    app.run(debug=True, port=5005)
