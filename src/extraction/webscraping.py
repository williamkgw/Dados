from selenium import webdriver
from selenium.webdriver.common.by import By

from time import sleep
import datetime
from pathlib import Path

def list_download_files_in_download_dir(download_dir):
    return list(download_dir.glob('*crdownload'))

def halt_for_download(download_dir, timeout):
    while not list_download_files_in_download_dir(download_dir):
        sleep(timeout/10)
        if list_download_files_in_download_dir(download_dir):
            break
        
    while list_download_files_in_download_dir(download_dir):
        sleep(timeout)

def init_driver(download_dir):
    chrome_driver_path = Path('/opt/homebrew/bin/chromedriver')
    download_dir_path_str = str(download_dir.resolve())
    prefs = {
        'download.prompt_for_download': False,
        'download.default_directory': download_dir_path_str,
        'download.directory_upgrage': True,
        'profile.default_content_settings.popups': 0,
    }
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('prefs', prefs)
    options.binary_location = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
    driver = webdriver.Chrome(executable_path = chrome_driver_path,options=options)
    return driver

def login_user(driver, email, password):
    login_box = driver.find_element(By.ID, 'l_usu_var_email')
    pass_box = driver.find_element(By.ID, 'l_usu_var_senha')
    login_button = driver.find_element(By.ID, 'btn_login')

    login_box.send_keys(email)
    pass_box.send_keys(password)

    driver.execute_script("arguments[0].click();", login_button)
    sleep(1)

    try:
        modal_body = driver.find_element(By.XPATH, '//div[@class="modal-body"]')
    except:
        return
    else:
        if modal_body.text == 'Email ou senha inválidos':
            raise Exception(f'{email} >> {password} Falha no Login/Senha')

def select_clinica(driver, nome_clinica):
    elems = driver.find_elements(By.TAG_NAME, 'h4')
    clinicas_dict = dict([(elem.text, elem) for elem in elems])

    clinica_button = clinicas_dict.get(nome_clinica, None)

    if clinica_button is None:
        raise Exception(f'{nome_clinica} not found')
    else:
        driver.execute_script("arguments[0].click();", clinica_button)

def select_vendas(driver):
    vendas_drop_list = driver.find_element(By.XPATH, '//span[normalize-space()="Vendas"]')
    driver.execute_script("arguments[0].click();", vendas_drop_list)
    sleep(0.5)

    vendas_dados = driver.find_element(By.XPATH, '(//a[normalize-space()="Consulta vendas"])')
    driver.execute_script("arguments[0].click();", vendas_dados)

def download_vendas(driver, end_date, download_dir):
    date_select = driver.find_element(By.XPATH, '//*[@id="p__ven_dat_data_text"]')
    driver.execute_script("arguments[0].click();", date_select)
    sleep(0.5)

    date_range_select = driver.find_element(By.XPATH, '//li[normalize-space()="Selecionar período"]')
    driver.execute_script("arguments[0].click();", date_range_select)
    sleep(0.5)

    timedelta = 2*datetime.timedelta(days = 365)
    beg_date  = (end_date - timedelta).replace(month = 1, day = 1)

    end_screen_date_element = driver.find_element(By.XPATH, '//div[@class="calendar right"]//th[@style = "width: auto"]')
    beg_screen_date_element = driver.find_element(By.XPATH, '//div[@class="calendar left"]//th[@style = "width: auto"]')

    end_screen_date = datetime.datetime.strptime(end_screen_date_element.text, '%B %Y').date()
    beg_screen_date = datetime.datetime.strptime(beg_screen_date_element.text, '%B %Y').date()

    def not_same_month_year(screen, reference):
        return screen.replace(day = 1) != reference.replace(day = 1)

    condition_beg = not_same_month_year(beg_screen_date, beg_date)
    condition_end = not_same_month_year(end_screen_date, end_date)

    while condition_beg:
        beg_screen_date_previous_month_element = driver.find_element(By.XPATH, '//div[@class="calendar left"]//th[@class="prev available"]')
        driver.execute_script("arguments[0].click();", beg_screen_date_previous_month_element)
        beg_screen_date_element = driver.find_element(By.XPATH, '//div[@class="calendar left"]//th[@style = "width: auto"]')
        beg_screen_date = datetime.datetime.strptime(beg_screen_date_element.text, '%B %Y').date()
        condition_beg = not_same_month_year(beg_screen_date, beg_date)

    sleep(0.5)
    beg_day_screen_date_element = driver.find_element(By.XPATH, 
            (
            '//div[@class="calendar left"]'
            f'//td[(@class="available " or @class="available active") and contains(@title, r) and normalize-space()="{beg_date.day}"]'
            )
    )
    driver.execute_script("arguments[0].click();", beg_day_screen_date_element)
    sleep(0.5)

    while condition_end:
        end_screen_date_previous_month_element = driver.find_element(By.XPATH, '//div[@class="calendar right"]//th[@class="prev available"]')
        driver.execute_script("arguments[0].click();", end_screen_date_previous_month_element)
        end_screen_date_element = driver.find_element(By.XPATH, '//div[@class="calendar right"]//th[@style = "width: auto"]')
        end_screen_date = datetime.datetime.strptime(end_screen_date_element.text, '%B %Y').date()
        condition_end = not_same_month_year(end_screen_date, end_date)

    sleep(0.5)
    end_day_screen_date_element = driver.find_element(By.XPATH, 
            (
            '//div[@class="calendar right"]'
            f'//td[(@class="available " or @class="available active") and contains(@title, r) and normalize-space()="{end_date.day}"]'
            )
    )
    driver.execute_script("arguments[0].click();", end_day_screen_date_element)
    sleep(0.5)

    pesq_button = driver.find_element(By.XPATH, '//button[@id="p__btn_filtrar"]')
    pesq_button.click()
    sleep(1)

    relatorio_button = driver.find_element(By.XPATH, '//button[@id="p__btn_relatorio"]')
    driver.execute_script("arguments[0].click();", relatorio_button)

    relatorio_csv_button = driver.find_element(By.XPATH, '//a[normalize-space()="Exportar para CSV"]')
    driver.execute_script("arguments[0].click();", relatorio_csv_button)

    halt_for_download(download_dir, 0.5)

def download_clientes(driver, download_dir):
    clientes_link = driver.find_element(By.XPATH, '//span[normalize-space()="Clientes"]')
    driver.execute_script("arguments[0].click();", clientes_link)
    sleep(3)

    relatorio_button = driver.find_element(By.XPATH, '//button[@id="p__btn_relatorio"]')
    driver.execute_script("arguments[0].click();", relatorio_button)
    sleep(0.5)

    relatorio_csv_button = driver.find_element(By.XPATH, '//a[normalize-space()="Exportar clientes para CSV"]')
    driver.execute_script("arguments[0].click();", relatorio_csv_button)
    halt_for_download(download_dir, 0.5)

    relatorio_button = driver.find_element(By.XPATH, '//button[@id="p__btn_relatorio"]')
    driver.execute_script("arguments[0].click();", relatorio_button)
    sleep(0.5)

    relatorio_csv_button = driver.find_element(By.XPATH, '//a[normalize-space()="Exportar clientes e animais para CSV"]')
    driver.execute_script("arguments[0].click();", relatorio_csv_button)
    halt_for_download(download_dir, 0.5)

def download(name, password, clinica, out_dir, end_date):
    import numpy as np

    site = 'https://app.simples.vet/login/login.php'

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

    out_dir.mkdir(parents = True, exist_ok = True)
    download_vendas(driver, end_date, out_dir)
    print(f'download_vendas finalizou {out_dir}')
    sleep(3)

    return_to_init_button = driver.find_element(By.XPATH, '//img[@alt="logo"]')
    driver.execute_script("arguments[0].click();", return_to_init_button)
    sleep(3)

    download_clientes(driver, out_dir)
    print(f'download_clientes finalizou {out_dir}')
    sleep(3)

    driver.quit()
