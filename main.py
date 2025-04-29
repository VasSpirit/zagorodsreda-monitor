import time
import logging
import os
import csv
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Настройки логирования
logging.basicConfig(
    filename='monitoring_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Настройка Chrome WebDriver
chrome_path = "C:\\chrome-win64\\chrome.exe"
chromedriver_path = os.path.abspath("C:\\Project\\zagorodsreda\\.venv\\chromedriver.exe")
service = Service(executable_path=chromedriver_path)

options = Options()
options.binary_location = chrome_path
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# Список URL объектов
urls = [
    "https://pos.gosuslugi.ru/lkp/fkgs/16455/94145/",
    "https://pos.gosuslugi.ru/lkp/fkgs/16455/94201/",
    "https://pos.gosuslugi.ru/lkp/fkgs/16455/94152/",
    "https://pos.gosuslugi.ru/lkp/fkgs/16455/94160/",
    "https://pos.gosuslugi.ru/lkp/fkgs/16455/94451/",
    "https://pos.gosuslugi.ru/lkp/fkgs/16455/94180/",
    "https://pos.gosuslugi.ru/lkp/fkgs/16455/94167/",
    "https://pos.gosuslugi.ru/lkp/fkgs/16455/96387/"
]

# Функция для извлечения информации
def extract_info(url):
    try:
        driver = webdriver.Chrome(service=service, options=options)
        logging.info(f"Открываем сайт: {url}")
        driver.get(url)

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "title")))
        title = driver.title
        logging.info(f"Заголовок страницы: {title}")

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "project-vote__container--address")))
        vote_number = driver.find_element(By.CLASS_NAME, "project-vote__container--address").text
        logging.info(f"Голоса: {vote_number}")

        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        logging.info(f"Дата получения информации: {current_time}")

        driver.quit()

        return {
            "title": title,
            "votes": vote_number,
            "timestamp": current_time,
        }

    except Exception as e:
        logging.error(f"Ошибка на странице {url}: {e}")
        return None


# Функция для сохранения данных в CSV
def save_to_csv(data):
    try:
        with open('votes_data.csv', mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ["title", "votes", "timestamp"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:
                writer.writeheader()
            writer.writerows(data)
        logging.info("Данные успешно сохранены в файл votes_data.csv.")
    except Exception as e:
        logging.error(f"Ошибка при сохранении данных в CSV: {e}")


# Сбор данных
collected_data = []
for url in urls:
    result = extract_info(url)
    if result:
        collected_data.append(result)

# Сохраняем собранные данные в CSV
if collected_data:
    save_to_csv(collected_data)
