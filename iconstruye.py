#! /usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
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
        options.add_argument("--headless")
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

        print(f'Extrayendo detalles de enlace {_id}...')
        try:
            enlace = obj.find_elements(By.TAG_NAME, "a")[0]
            enlace.click()
        except StaleElementReferenceException:
            return None

        element = self.wait.until(EC.visibility_of_element_located((By.ID, 'tblDetalle')))
        tblDetalle  = self.browser.find_element(By.ID, 'tblDetalle')

        print('tblDetalle obtenida')
        time.sleep(2)
        
        rows = tblDetalle.find_elements(By.TAG_NAME, "tr")
        detalles = []
        master = {}
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 9:
                master = {
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
                        'glosa':cells[9].text
                        }
                detalles.append(master)
            elif len(cells) == 7:
                try:
                    slave = {
                            'nomina_id':master['nomina_id'],
                            'no_grupo':master['no_grupo'],
                            'rut_proveedor':master['rut_proveedor'],
                            'razon_social':master['razon_social'],
                            'total_a_pagar_por_proveedor':master['total_a_pagar_por_proveedor'],
                            'no_documento':cells[0].text,
                            'tipo_documento':cells[1].text,
                            'fecha_emision':cells[2].text,
                            'total_a_pagar_por_documento':cells[3].text,
                            'forma_de_pago':cells[4].text,
                            'glosa':cells[5].text
                            }
                    detalles.append(slave)
                except Exception as e:
                    print(master, _id)
                    print(e)
            else:
                continue

        print('Hecho')
        return detalles

    def next_pagination(self):
        '''
        Obtiene los elementos de paginacion
        '''
        
        element = self.wait.until(EC.visibility_of_element_located((By.ID, 'Table1')))
        tabla_pagination = self.browser.find_element(By.ID, 'Table1')
        row = tabla_pagination.find_elements(By.TAG_NAME, "tr")[0]
        bloques = row.find_elements(By.TAG_NAME, "td")
        
        if len(bloques) == 3:
            link = bloques[2].find_elements(By.TAG_NAME, "a")[0]
            return link
        else:
            return None
                                                            
    def extraer_nominas_generales(self) -> list:
        '''
        Extraer enlaces de las nominas generales
        '''

        print('Extrayendo enlaces...')
        enlaces = []

        ind = 0
        real_ind = 0
        while True:

            ind += 1
            real_ind += 1

            if real_ind == 51:
                real_ind = 1
                
                next_btn = self.next_pagination()
                if next_btn:
                    print('Llevando a proxima pagina')
                    next_btn.click()
                else:
                    break
                
            print('Cargando tabla_nominas...')
            element = self.wait.until(EC.visibility_of_element_located((By.ID, 'tblNominas')))
            tabla_nominas = self.browser.find_element(By.ID, 'tblNominas')

            rows = tabla_nominas.find_elements(By.TAG_NAME, "tr")
            total_rows = len(rows)
            
            if real_ind == total_rows:
                break
            
            row = rows[real_ind]
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
                detalles_finales = []
                l = enlaces[-1]
                detalle = self.detalle_de_enlace(obj=l.get('opciones'), _id=l.get('id'))
                detalles_finales.append(detalle)
                self.agregar_detalle_csv(filename='nominas_detalle.csv', data=detalles_finales, first_time=True if ind==1 else False)
                self.browser.back()
        self.agregar_nominas(filename='nomina_general.csv', data=enlaces)
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

    def agregar_detalle_csv(self, filename:str, data:list, first_time:bool=True):
        '''
        Crear archivo CSV con los datos
        '''
        print('Creando CSV Detalle...')
        
        with open(filename, mode='a', newline='') as file:
            # -- Obtener los titulos de las celdas
            headers = data[0][0].keys()
            
            # -- Constructor de CSV
            writer = csv.DictWriter(file, fieldnames=headers)
            if first_time:
                writer.writeheader()

            # -- Escribir los datos en el archivo
            for lista in data:
                for row in lista:
                    writer.writerow(row)
                
        print('Hecho')
        
    def agregar_nominas(self, filename:str, data:list):
        '''
        Crear archivo CSV con los datos
        '''
        print('Creando CSV...')
        with open(filename, mode='a', newline='') as file:
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


file = open('nomina_general.csv', mode='w')
file.close()
file = open('nominas_detalle.csv', mode='w')
file.close()

ic = iConstruye(ChromeBrowser())
ic.login(url='https://cl.iconstruye.com/loginsso.aspx?hsCtaTracking=c5739d9b-1567-4a49-90d4-9e8e1701f105%7Cc9ffe135-4402-4101-a071-33ca6e5227d4')
time.sleep(5)
ic.listar_nomina(url="https://cl.iconstruye.com/Nomina/Inactiva/listar.aspx")
time.sleep(2)

enlaces = ic.extraer_nominas_generales()

time.sleep(3)
ic.browser.quit()
del ic
