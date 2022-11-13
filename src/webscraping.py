from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

import pandas as pd

from time import sleep
import datetime
import locale

from pathlib import Path

def init_driver(out_dir):
    chrome_driver_path    = Path('thirdparty/chromedriver_win32/chromedriver.exe')
    print(out_dir)

    prefs = dict([('download.default_directory', str(out_dir.resolve()))])
    print(prefs)

    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(executable_path = chrome_driver_path,options=options)
    return driver

def login_user(driver, name, password):
    login_box = driver.find_element(By.ID, 'l_usu_var_email')
    pass_box = driver.find_element(By.ID, 'l_usu_var_senha')
    login_button = driver.find_element(By.ID, 'btn_login')

    login_box.send_keys(name)
    pass_box.send_keys(password)
    driver.execute_script("arguments[0].click();", login_button)

def select_clinica(driver, clinica):
    elems = driver.find_elements_by_tag_name('h4')
    clinicas_dict = dict([(elem.text, elem) for elem in elems])
    
    clinica_button = clinicas_dict.get(clinica, None)
    
    if clinica_button is None:
        print(f'{clinica} not found')
    else:
        driver.execute_script("arguments[0].click();", clinica_button)

def select_vendas(driver):

    vendas_drop_list = driver.find_element(By.XPATH, '//span[normalize-space()="Vendas"]')
    driver.execute_script("arguments[0].click();", vendas_drop_list)
    sleep(0.5)

    vendas_link = driver.find_element(By.XPATH, '(//a[@class="link-menu"][normalize-space()="Vendas"])[1]')
    driver.execute_script("arguments[0].click();", vendas_link)

def download_vendas(driver):

    date_select = driver.find_element(By.XPATH, '//*[@id="p__ven_dat_data_text"]')
    driver.execute_script("arguments[0].click();", date_select)
    sleep(0.5)

    date_range_select = driver.find_element(By.XPATH, '//li[normalize-space()="Selecionar período"]')
    driver.execute_script("arguments[0].click();", date_range_select)
    sleep(0.5)

    timedelta = 2*datetime.timedelta(days = 365)
    end_date  = datetime.date(day = 31, month = 10, year = 2022)
    beg_date  = (end_date - timedelta).replace(month = 1, day = 1)

    end_screen_date_element = driver.find_element(By.XPATH, '//div[@class="calendar right"]//th[@style = "width: auto"]')
    beg_screen_date_element = driver.find_element(By.XPATH, '//div[@class="calendar left"]//th[@style = "width: auto"]')

    end_screen_date = datetime.datetime.strptime(end_screen_date_element.text, '%B %Y').date()
    beg_screen_date = datetime.datetime.strptime(beg_screen_date_element.text, '%B %Y').date()

    not_same_month_year = lambda screen, reference: screen.replace(day = 1) != reference.replace(day = 1)

    condition_beg = not_same_month_year(beg_screen_date, beg_date)
    condition_end = not_same_month_year(end_screen_date, end_date)
    one_month = datetime.timedelta(days = 30)

    while condition_end:
        while condition_beg:

            beg_screen_date_previous_month_element = driver.find_element(By.XPATH, '//div[@class="calendar left"]//th[@class="prev available"]')
            driver.execute_script("arguments[0].click();", beg_screen_date_previous_month_element)
            beg_screen_date_element = driver.find_element(By.XPATH, '//div[@class="calendar left"]//th[@style = "width: auto"]')
            beg_screen_date = datetime.datetime.strptime(beg_screen_date_element.text, '%B %Y').date()
            condition_beg = not_same_month_year(beg_screen_date, beg_date)
        
        beg_day_screen_date_element = driver.find_element(By.XPATH, f'//div[@class="calendar left"]//td[normalize-space()="{beg_date.day}"]')
        driver.execute_script("arguments[0].click();", beg_day_screen_date_element)

        end_screen_date_previous_month_element = driver.find_element(By.XPATH, '//div[@class="calendar right"]//th[@class="prev available"]')
        driver.execute_script("arguments[0].click();", end_screen_date_previous_month_element)
        end_screen_date_element = driver.find_element(By.XPATH, '//div[@class="calendar right"]//th[@style = "width: auto"]')
        end_screen_date = datetime.datetime.strptime(end_screen_date_element.text, '%B %Y').date()
        condition_end = not_same_month_year(end_screen_date, end_date)
    
    end_day_screen_date_element = driver.find_element(By.XPATH, f'//div[@class="calendar right"]//td[normalize-space()="{end_date.day}"]')
    driver.execute_script("arguments[0].click();", end_day_screen_date_element)

    relatorio_button = driver.find_element(By.XPATH, '//button[@id="p__btn_relatorio"]')
    relatorio_button.click()
    sleep(0.5)

    relatorio_csv_button = driver.find_element(By.XPATH, '//a[normalize-space()="Exportar para CSV"]')
    driver.execute_script("arguments[0].click();", relatorio_csv_button)
    sleep(45)

def download_clientes(driver):

    clientes_link = driver.find_element(By.XPATH, '//span[normalize-space()="Clientes"]')
    driver.execute_script("arguments[0].click();", clientes_link)
    sleep(3)

    relatorio_button = driver.find_element(By.XPATH, '//button[@id="p__btn_relatorio"]')
    driver.execute_script("arguments[0].click();", relatorio_button)
    sleep(0.5)

    relatorio_csv_button = driver.find_element(By.XPATH, '//a[normalize-space()="Exportar clientes para CSV"]')
    driver.execute_script("arguments[0].click();", relatorio_csv_button)
    sleep(15)


def login(name, password, clinica, out_dir):
    import numpy as np

    site = 'https://app.simples.vet/login/login.php'
    locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')

    driver = init_driver(out_dir)
    driver.get(site)
    sleep(1)

    login_user(driver, name, password)
    sleep(1)

    if clinica is not np.nan:
        select_clinica(driver, clinica)
        sleep(3)

    select_vendas(driver)
    sleep(3)

    download_vendas(driver)
    sleep(3)

    return_to_init_button = driver.find_element(By.XPATH, '//img[@alt="logo"]')
    driver.execute_script("arguments[0].click();", return_to_init_button)
    sleep(3)

    download_clientes(driver)
    sleep(3)

    driver.quit()

def get_all_logins(filename, emps):

    import numpy as np

    input_dir = Path('data/input/22_dados')

    acess_pass_df = pd.read_excel(filename)
    acess_pass_df = acess_pass_df[acess_pass_df['SITES'] == 'SIMPLESVET']

    for index, row in acess_pass_df.iterrows(): 
        emp         = row['EMPRESA']
        if emp in emps:
            print(emp)
            nome_acesso = row['NOME DE ACESSO']
            acesso      = row['ACESSO']
            senha       = row['SENHA']
            extra       = row['EXTRA']

            if extra is np.nan:
                output_dir = input_dir / f'{emp}/Carga/2022/10 - Outubro'
                output_dir.mkdir(parents = True, exist_ok = True)
                login(acesso, senha, nome_acesso, output_dir)
            elif extra is not np.nan:
                output_dir = input_dir / f'{emp}/Carga/2022/10 - Outubro/{extra}'
                output_dir.mkdir(parents = True, exist_ok = True)
                login(acesso, senha, nome_acesso, output_dir)

def main(): 
    emps = ['Amor de Bichos - MG', 'Animed RS', 'Arca de Noé - ES', 'Burlina', 'CatsIndoor', 'Cia Veterinária RJ', 'EBVet', 'Fórmula Pet', 'Almir Tavares', 'Mania Animal', 'Mundo Silvestre', 'MyVet - Morumbi - SP', 'Pupim', 'Tierplatz RS', 'Vet dos Anjos SP', 'VetCenter MT']
    # get_all_logins('passwords_acess_system.xlsx', emps)
    



if __name__ == '__main__':
    main()