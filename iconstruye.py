#! /usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import urllib.request
import os
#import pycurl
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=200)
user_agent_rotator.get_user_agents()

class FirefoxBrowser(object):
    user_agent = ''

    def __init__(self):
        FirefoxBrowser.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/43.4'
        #https://www.geeksforgeeks.org/http-headers-user-agent/
        #https://deviceatlas.com/blog/list-of-user-agent-strings
        #user_agent = user_agent_rotator.get_random_user_agent()
        
    def get_browser(self):
        profile = webdriver.FirefoxProfile()
        profile.accept_untrusted_certs = True
        options = Options()
        #options.add_argument("--headless")

        options.add_argument(f'User-Agent={FirefoxBrowser.user_agent}')

        return webdriver.Firefox(options=options, firefox_profile=profile)

        
class ChromeBrowser(object):
    user_agent = ''
    
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/43.4'
        
    def get_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument('ignore-certificate-errors')
        return webdriver.Chrome(options=options)
    

class iConstruye(object):
    """
    Extraccion de datos desde pagina iconstruye
    """

    def __init__(self, browser):
        self.browser = browser.get_browser()
        
    def __open_page(self, url):
        print('Cargando url,espere un momento...')
        self.browser.get(url)

    def login(self, url):
        self.__open_page(url=url)

    def get_data(self):
        self.__open_page(url=self.url)
        items = self.browser.find_elements_by_css_selector('.item-page ul')
        
        ind = -1
        if len(items)>0:
            print('Revisando items, espere...')
            for ul in items:
                ind +=1
                for li in ul.find_elements_by_css_selector('li'):
                    #-- Obtiene el conteido del elemento <li>, lo secciona por espacios y toma el ultimo elemento que es el ano
                    #-- Ejemplo : Resumen estadístico Feminicidio y Tentativas 2020 -> 2020
                    file_name = li.text.split(' ')[-1].strip()
                    url = li.find_elements_by_css_selector('a')[0].get_attribute('href')
                    #-- Obtiene la extension del archivo y la agrega al nombre corto que le dimos al archivo
                    ext = url.split('.')[-1]
                    file_name += '.'+ext
        else:
            print('No se encontraron ITEMS')
  
ic = iConstruye(FirefoxBrowser())
ic.login(url='https://cl.iconstruye.com/loginsso.aspx?hsCtaTracking=c5739d9b-1567-4a49-90d4-9e8e1701f105%7Cc9ffe135-4402-4101-a071-33ca6e5227d4')