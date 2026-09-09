import os
import pytest
import requests

@pytest.fixture
def token():
    # Робот Гитхаба сам возьмет токен из секретов, которые мы настроили
    token_value = os.getenv("YANDEX_TOKEN")
    if not token_value:
        pytest.fail("Токен не найден в переменных окружения!")
    return token_value

# ТЕСТ 1: Проверка метода GET (Связь с Яндекс Диском)
def test_yandex_disk_connection(token):
    url = "https://yandex.net"
    headers = {"Authorization": f"OAuth {token}"}
    
    response = requests.get(url, headers=headers)
    assert response.status_code == 200

# ТЕСТ 2: Полный цикл — Создание папки (POST), Загрузка файла (PUT) и Удаление (DELETE)
def test_yandex_disk_full_lifecycle(token):
    headers = {"Authorization": f"OAuth {token}"}
    folder_url = "https://yandex.net/resources"
    folder_path = "Yandex_Stazhirovka_Test_Folder"
    file_path = f"{folder_path}/test_file.txt"
    
    # 1. СОЗДАЕМ ПАПКУ (PUT-запрос в API Яндекса для ресурсов)
    create_dir_res = requests.put(folder_url, headers=headers, params={"path": folder_path})
    assert create_dir_res.status_code == 201

    # 2. ЗАПРАШИВАЕМ ССЫЛКУ НА ЗАГРУЗКУ ФАЙЛА (GET)
    upload_url = "https://yandex.net/resources/upload"
    upload_res = requests.get(upload_url, headers=headers, params={"path": file_path, "overwrite": "true"})
    assert upload_res.status_code == 200
    href = upload_res.json().get("href")

    # 3. ЗАГРУЖАЕМ ФАЙЛ НА ДИСК (PUT по полученной ссылке href)
    file_content = b"Hello, Yandex Team! This is automated test file."
    put_file_res = requests.put(href, data=file_content)
    assert put_file_res.status_code == 201

    # 4. ПРОВЕРЯЕМ, ЧТО ФАЙЛ СУЩЕСТВУЕТ НА ДИСКЕ (GET)
    check_file_res = requests.get(folder_url, headers=headers, params={"path": file_path})
    assert check_file_res.status_code == 200
    assert check_file_res.json().get("type") == "file"

    # 5. ОЧИЩАЕМ ДИСК ЗА СОБОЙ — УДАЛЯЕМ ПАПКУ И ВСЁ ВНУТРИ (DELETE)
    delete_res = requests.delete(folder_url, headers=headers, params={"path": folder_path})
    assert delete_res.status_code in [202, 204]
