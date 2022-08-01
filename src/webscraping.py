from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

site = 'https://app.simples.vet/login/login.php'

def init_driver():
    chrome_driver_path = r'thirdparty/chromedriver_win32/chromedriver.exe'
    default_download_path = r'C:\Users\willi\Desktop\clinica_exemplo\download'

    prefs = dict([('download.default_directory', default_download_path)])

    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(executable_path = chrome_driver_path,options=options)
    return driver

def login(name, password):
    driver = init_driver()
    driver.get(site)
    time.sleep(0.5)

    login_box = driver.find_element(By.NAME, 'l_usu_var_email')
    pass_box = driver.find_element(By.NAME, 'l_usu_var_senha')
    login_button = driver.find_element(By.ID, 'btn_login')

    login_box.send_keys(name)
    pass_box.send_keys(password)
    
    login_button.click()
    time.sleep(1)
    
    clinica_exemplo_button = driver.find_element(By.XPATH, '//*[@id="ambientes"]/div[1]/div/div')
    clinica_exemplo_button.click()
    time.sleep(4)

    vendas_button = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/ul/li[5]/a')
    vendas_button.click()
    time.sleep(4)

    vendas_button = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/ul/li[5]/ul/li[4]/a')
    vendas_button.click()
    time.sleep(4)

    relatorio_button = driver.find_element(By.XPATH, '//*[@id="p__btn_relatorio"]')
    relatorio_button.click()
    time.sleep(4)

    relatorio_button = driver.find_element(By.XPATH, '//*[@id="filter"]/span/ul/li[7]/a')
    relatorio_button.click()
    time.sleep(4)

    driver.quit()
