import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from tkinter import Tk, simpledialog

# Функция для запроса у пользователя поискового запроса
def get_search_query():
    root = Tk()
    root.withdraw()  # Скрыть основное окно
    query = simpledialog.askstring("Поисковый запрос", "Что вы ищете?")
    return query

# Задаем путь к директории для сохранения файла
save_directory = "/gmpscanner"  # Замените на нужный путь
file_path = os.path.join(save_directory, 'gmpscanner_out.txt')

# Устанавливаем драйвер для Firefox
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

try:
    # Запрос у пользователя поискового запроса
    search_query = get_search_query()
    if not search_query:
        print("Поисковый запрос не был введен.")
        driver.quit()
        exit()

    # Открываем Google Maps
    driver.get("https://www.google.com/maps")

    # Ждем загрузки страницы и строки поиска
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='searchboxinput']")))

    # Находим строку поиска и вводим запрос пользователя
    search_box = driver.find_element(By.XPATH, "//input[@id='searchboxinput']")
    search_box.send_keys(search_query)  # Вводим запрос пользователя
    search_box.send_keys(Keys.RETURN)  # Нажимаем Enter

    # Ждем загрузки результатов поиска
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@class='hfpxzc']")))

    links = []
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(links) < 50:  # Увеличиваем до 50 результатов
        # Прокручиваем страницу вниз для загрузки дополнительных результатов
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Ждем, чтобы новые результаты успели подгрузиться

        # Получаем ссылки на рестораны
        results = driver.find_elements(By.XPATH, "//a[@class='hfpxzc']")

        # Добавляем уникальные ссылки в список
        for result in results:
            link = result.get_attribute("href")
            if link not in links:  # Избегаем дубликатов
                links.append(link)

        # Проверяем высоту страницы, чтобы понять, закончилась ли прокрутка
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # Если высота страницы не изменилась, выходим
            break
        last_height = new_height

    # Ограничиваем до 50 результатов, если собрано больше
    links = links[:50]

    # Сохранение ссылок в файл
    with open(file_path, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(link + '\n')

    print(f"Ссылки на рестораны сохранены в {file_path}")

except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    # Закрываем браузер
    driver.quit()
