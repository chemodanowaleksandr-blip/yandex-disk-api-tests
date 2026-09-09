import os
import pytest
import requests

@pytest.fixture
def token():
    return os.getenv("YANDEX_TOKEN")

def test_yandex_disk_connection(token):
    url = "https://yandex.net"
    res = requests.get(url, headers={"Authorization": f"OAuth {token}"})
    assert res.status_code == 200

def test_yandex_disk_full_lifecycle(token):
    h = {"Authorization": f"OAuth {token}"}
    base_url = "https://yandex.netresources"
    
    _path = "Yandex_Stazhirovka_Test_Folder"
    file_path = f"{_path}/test_file.txt"
    
    # 1. Создаем папку
    assert requests.put(base_url, headers=h, params={"path": _path}).status_code == 201
    
    # 2. Получаем ссылку для загрузки файла
    upload_url = "https://yandex.netresources/upload"
    upload_res = requests.get(upload_url, headers=h, params={"path": file_path, "overwrite": "true"})
    assert upload_res.status_code == 200
    href = upload_res.json().get("href")
    
    # 3. Загружаем сам файл по полученной ссылке
    assert requests.put(href, data="Hello Yandex!").status_code == 201
    
    # 4. Проверяем, что файл действительно появился
    check_res = requests.get(base_url, headers=h, params={"path": file_path})
    assert check_res.status_code == 200 and check_res.json().get("type") == "file"
    
    # 5. Удаляем созданную папку со всеми файлами внутри
    assert requests.delete(base_url, headers=h, params={"path": _path}).status_code in [202, 204]
