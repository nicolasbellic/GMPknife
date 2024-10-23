import csv
import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from tkinter import Tk, filedialog

# Функция для выбора текстового файла
def choose_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    return file_path

# Функция для выбора директории
def choose_directory():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    return folder_selected

# Устанавливаем драйвер для Firefox
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

try:
    links_file_path = choose_file()
    save_directory = choose_directory()
    file_path = os.path.join(save_directory, 'gmpknife_out.csv')

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Название', 'Ссылка', 'Рейтинг', 'Количество отзывов', 'Ссылки на фотографии'])

        with open(links_file_path, 'r', encoding='utf-8') as links_file:
            links = links_file.readlines()

        for link in links:
            link = link.strip()
            if not link:
                continue

            driver.get(link)

            try:
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//h1")))
                name = driver.find_element(By.XPATH, "//h1").text
                restaurant_link = link

                try:
                    rating = driver.find_element(By.XPATH, "//span[contains(@class, 'MW4etd')]").text
                except:
                    rating = "Рейтинг не найден"

                # Получение количества отзывов
                try:
                    reviews = driver.find_element(By.XPATH, "//span[contains(@class, 'UY7F9')]").text  # Обновите XPath, если нужно
                except:
                    reviews = "Количество отзывов не найдено"

                photo_links = []
                time.sleep(2)
                photo_elements = driver.find_elements(By.XPATH, "//img[contains(@class, 'n4y2n')]")
                for i, photo in enumerate(photo_elements):
                    photo_url = photo.get_attribute("src")
                    if photo_url:
                        photo_links.append(photo_url)

                        response = requests.get(photo_url)
                        photo_filename = f"{name.replace(' ', '_').replace('/', '_')}_photo_{i + 1}.jpg"
                        photo_path = os.path.join(save_directory, photo_filename)

                        with open(photo_path, 'wb') as img_file:
                            img_file.write(response.content)

                writer.writerow([name, restaurant_link, rating, reviews, ', '.join(photo_links)])

            except Exception as e:
                print(f'Ошибка при обработке ссылки {link}: {e}')

finally:
    driver.quit()
