import time
import pytest
from settings import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located as find_element
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located as find_elements


@pytest.fixture
def setup():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--window-size=1200,800')
    pytest.driver = webdriver.Chrome(options=options)
    time.sleep(5)
    # Переходим на страницу авторизации
    pytest.driver.get('http://petfriends.skillfactory.ru/login')
    pytest.wait = WebDriverWait(pytest.driver, 10)


def test_show_my_pets(setup):
    # Вводим email
    pytest.wait.until(find_element((By.ID, "email"))).send_keys(valid_email)
    # Вводим пароль
    pytest.wait.until(find_element((By.ID, "pass"))).send_keys(valid_password)
    # Нажимаем на кнопку входа в аккаунт
    pytest.wait.until(find_element((By.CSS_SELECTOR, 'button[type="submit"]'))).click()
    # Проверяем, что мы оказались на главной странице пользователя
    assert pytest.wait.until(find_element((By.TAG_NAME, 'h1'))).text == "PetFriends"
    pytest.wait.until(find_element((By.XPATH, '//a[text()="Мои питомцы"]'))).click()
    assert pytest.wait.until(find_element((By.TAG_NAME, 'h2'))).text == user_name


def test_check_present_all_pets():
    # получаем элемент с количеством питомцев
    count_all_pets = pytest.wait.until(find_element((By.XPATH, '//div[@class=".col-sm-4 left"]'))).text
    # получаем счётчик питомцев
    pytest.count_all_pets = int(count_all_pets.split('\n')[1].split(': ')[1])
    # получаем список всех карточек питомцев
    cards_all_pets = pytest.wait.until(find_elements((By.XPATH, '//tbody/tr')))
    # сравниваем счётчик с количеством питомцев
    assert pytest.count_all_pets == len(cards_all_pets)


def test_half_pets_have_photo():
    # счётчик питомцев с фото
    count_pets_with_photo = 0
    # получаем все элементы для хранения фото питомцев
    images = pytest.wait.until(find_elements((By.XPATH, '//th[@scope="row"]/img')))
    # считаем сколько элементов с фото внутри
    for image in images:
        if image.get_attribute('src'):
            count_pets_with_photo += 1
    # считаем процент питомцев с фото
    percent_pets_with_photo = count_pets_with_photo * 100 / pytest.count_all_pets
    # проверяем соответствие условию теста
    try:
        assert percent_pets_with_photo >= 50
    except AssertionError:
        print('!!!ВНИМАНИЕ!!!\n Менее половины питомцев имеют фото')


def test_fields_not_empty():
    # получаем данные о питомцах
    names = pytest.wait.until(find_elements((By.XPATH, '//tbody/tr/td[1]')))
    animal_types = pytest.wait.until(find_elements((By.XPATH, '//tbody/tr/td[2]')))
    ages = pytest.wait.until(find_elements((By.XPATH, '//tbody/tr/td[3]')))
    # проверяем, что поля питомцев не пустые
    try:
        for i in range(len(names)):
            assert names[i].text != ''
            assert animal_types[i].text != ''
            assert ages[i].text != ''
    except AssertionError:
        print(f'!!!ВНИМАНИЕ!!!\n Есть питомец с пустым полем')


def test_all_pets_have_different_names():
    # получаем список элементов, хрянящих имена
    element_names = pytest.wait.until(find_elements((By.XPATH, '//tbody/tr/td[1]')))
    # список для хранения имён
    names = []
    # наполняем именами список
    for name in element_names:
        names.append(name.text)

    # сравниваем количество уникальных имён с количеством всех имён
    try:
        assert len(names) == len(set(names))
    except AssertionError:
        print('!!!ВНИМАНИЕ!!!\nНе у всех питомцев разные имена')


def test_all_pets_are_unique():
    # получаем данные о питомцах
    names = pytest.wait.until(find_elements((By.XPATH, '//tbody/tr/td[1]')))
    animal_types = pytest.wait.until(find_elements((By.XPATH, '//tbody/tr/td[2]')))
    ages = pytest.wait.until(find_elements((By.XPATH, '//tbody/tr/td[3]')))

    # Создаём список с данными о питомцах
    pets = []
    for i in range(len(names)):
        pet = [names[i].text, animal_types[i].text, ages[i].text]
        pets.append(pet)

    # Подготавливаем список из строк, чтобы проверить на уникальность питомцев
    string_pets = []
    for pet in pets:
        string_pets.append(str(pet))
    # Оставляем только уникальных питомцев
    unique_pets = set(string_pets)
    # Сравниваем длины исходного и уникального списка питомцев
    try:
        assert len(pets) == len(set(unique_pets))
    except AssertionError:
        print('!!!ВНИМАНИЕ!!!\nЕсть повторяющиеся питомцы')
    # Поскольку тест последний, то закрываем браузер
    pytest.driver.quit()
