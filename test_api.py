import os
import pytest
import requests

@pytest.fixture
def token():
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

# ТЕСТ 2: Полный цикл — Создание папки, Загрузка файла и Удаление
def test_yandex_disk_full_lifecycle(token):
    headers = {"Authorization": f"OAuth {token}"}
    base_url = "https://yandex.net/resources"
    folder_path = "Yandex_Stazhirovka_Test_Folder"
    file_path = f"{folder_path}/test_file.txt"
    
    # 1. СОЗДАЕМ ПАПКУ (PUT)
    create_dir_res = requests.put(base_url, headers=headers, params={"path": folder_path})
    assert create_dir_res.status_code == 201

    # 2. ЗАПРАШИВАЕМ ССЫЛКУ НА ЗАГРУЗКУ ФАЙЛА (GET)
    upload_url = "https://yandex.net/resources/upload"
    upload_res = requests.get(upload_url, headers=headers, params={"path": file_path, "overwrite": "true"})
    assert upload_res.status_code == 200
    href = upload_res.json().get("href")

    # 3. ЗАГРУЖАЕМ ФАЙЛ НА ДИСК (PUT)
    file_content = b"Hello, Yandex Team! This is automated test file."
    put_file_res = requests.put(href, data=file_content)
    assert put_file_res.status_code == 201

    # 4. ПРОВЕРЯЕМ, ЧТО ФАЙЛ СУЩЕСТВУЕТ (GET)
    check_file_res = requests.get(base_url, headers=headers, params={"path": file_path})
    assert check_file_res.status_code == 200
    assert check_file_res.json().get("type") == "file"

    # 5. ОЧИЩАЕМ ДИСК ЗА СОБОЙ (DELETE)
    delete_res = requests.delete(base_url, headers=headers, params={"path": folder_path})
    assert delete_res.status_code in [202, 204]
