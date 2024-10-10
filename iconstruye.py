#! /usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import csv
from dotenv import load_dotenv

load_dotenv()

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
        self.wait = WebDriverWait(self.browser, 5)
        
    def __open_page(self, url:str):
        '''
        Abre una pagina web
        '''

        print('Cargando url,espere un momento...')
        self.browser.get(url)

    def detalle_de_enlace(self, obj:object, _id:int) -> list:
        '''
        Abre la lupa de este elemento
        '''

        print('Extrayendo detalles de enlace...')
        enlace = obj.find_elements(By.TAG_NAME, "a")[0]
        enlace.click()

        element = self.wait.until(EC.visibility_of_element_located((By.ID, 'tblDetalle')))
        tblDetalle  = self.browser.find_element(By.ID, 'tblDetalle')

        print('tblDetalle obtenida')
        print(tblDetalle)
        time.sleep(2)
        
        rows = tblDetalle.find_elements(By.TAG_NAME, "tr")
        detalles = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 9:
                detalles.append({
                                'nomina_id':_id,
                                'no_grupo':cells[0].text,
                                'rut_proveedor':cells[1].text,
                                'razon_social':cells[2].text,
                                'total_a_pagar_por_proveedor':cells[3].text,
                                'no_documento':cells[4].text,
                                'tipo_documento':cells[5].text,
                                'fecha_emision':cells[6].text,
                                'total_a_pagar_por_documento':cells[7].text,
                                'forma_de_pago':cells[8].text,
                                'glosa':cells[9].text})
        print('Hecho')
        return detalles

    def extraer_enlaces_tabla(self) -> list:
        '''
        Extraer enlaces de la tabla
        '''
        
        print('Extrayendo enlaces...')
        enlaces = []
        element = self.wait.until(EC.visibility_of_element_located((By.ID, 'tblNominas')))
        tabla_nominas = self.browser.find_element(By.ID, 'tblNominas')

        print('GET tabla_nominas')
        #wait = WebDriverWait(self.browser, 10)
        #pagination = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pagination')))
        #pages = pagination.find_elements(By.TAG_NAME, "a")
        #page_numbers = []
        #for page in pages:
        #    page.click()

        rows = tabla_nominas.find_elements(By.TAG_NAME, "tr")
        ind = 0
        for row in rows[1:]:
            ind += 1
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 10:
                enlaces.append({
                                'id':ind,
                                'fecha_carga':cells[0].text,
                                'numero':cells[1].text,
                                'fecha_pago':cells[2].text,
                                'entidad_pago':cells[3].text,
                                'total_pagar':cells[4].text,
                                'cantidad_proveedores':cells[5].text,
                                'cantidad_documentos':cells[6].text,
                                'estado_nomina':cells[7].text,
                                'estado_publicacion':cells[8].text,
                                'opciones':cells[9]})
        print('Hecho')
        return enlaces
        
    def listar_nomina(self, url):
        '''
        Listar las nóminas
        '''

        self.__open_page(url=url)
        print('Listando nominas...')
        element = self.wait.until(EC.visibility_of_element_located((By.ID, 'btnBuscar')))
        btn_buscar = self.browser.find_element(By.ID, 'btnBuscar')
        btn_buscar.click()

        print('Hecho')

    def crear_csv_detalle(self, filename:str, data:list):
        '''
        Crear archivo CSV con los datos
        '''
        print('Creando CSV Detalle...')
        
        with open(filename, mode='w', newline='') as file:
            # -- Obtener los titulos de las celdas
            headers = data[0][0].keys()
            
            # -- Constructor de CSV
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            # -- Escribir los datos en el archivo
            for lista in data:
                for row in lista:
                    writer.writerow(row)
                
        print('Hecho')
        
    def crear_csv(self, filename:str, data:list):
        '''
        Crear archivo CSV con los datos
        '''
        print('Creando CSV...')
        with open(filename, mode='w', newline='') as file:
            # -- Obtener los titulos de las celdas
            headers = data[0].keys()

            # -- Constructor de CSV
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            # -- Escribir los datos en el archivo
            for row in data:
                new_row = row.copy()
                new_row.update({'opciones':'-'})
                writer.writerow(new_row)
        print('Hecho')

    def login(self, url):
        self.__open_page(url=url)

        # -- Definir los campos
        username = self.browser.find_element(By.ID, 'txtUsuarioUOC')
        password = self.browser.find_element(By.ID, 'txtPasswordUOC')
        organizacion = self.browser.find_element(By.ID, 'txtOrganizacionUOC')
    
        # -- Llenar los campos
        username.send_keys(os.getenv('usuario'))
        password.send_keys(os.getenv('password'))
        organizacion.send_keys(os.getenv('organizacion'))

        # -- Dar clic en boton Login
        self.browser.find_element(By.ID, 'btnIniciaSessionUOC').click()

ic = iConstruye(ChromeBrowser())
ic.login(url='https://cl.iconstruye.com/loginsso.aspx?hsCtaTracking=c5739d9b-1567-4a49-90d4-9e8e1701f105%7Cc9ffe135-4402-4101-a071-33ca6e5227d4')
time.sleep(5)
ic.listar_nomina(url="https://cl.iconstruye.com/Nomina/Inactiva/listar.aspx")
time.sleep(2)

enlaces = ic.extraer_enlaces_tabla()
ic.crear_csv(filename='nomina_general.csv', data=enlaces)

detalles_finales = []
for l in enlaces:
    detalle = ic.detalle_de_enlace(obj=l.get('opciones'), _id=l.get('id'))
    detalles_finales.append(detalle)
    ic.browser.back()

ic.crear_csv_detalle(filename='nominas_detalle.csv', data=detalles_finales)

time.sleep(3)
ic.browser.quit()
