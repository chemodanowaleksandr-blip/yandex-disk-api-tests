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
    headers = {"Authorization": f"OAuth {token}"}
    api_url = "https://yandex.netresources"
    
    folder_name = "Yandex_Stazhirovka_Test_Folder"
    file_path = f"{folder_name}/test_file.txt"
    
    # 1. Создаем папку
    res_mkdir = requests.put(api_url, headers=headers, params={"path": folder_name})
    assert res_mkdir.status_code == 201
    
    # 2. Получаем ссылку для загрузки файла
    upload_url = "https://yandex.netresources/upload"
    res_upload_link = requests.get(upload_url, headers=headers, params={"path": file_path, "overwrite": "true"})
    assert res_upload_link.status_code == 200
    href = res_upload_link.json().get("href")
    
    # 3. Загружаем сам файл по полученной ссылке
    res_upload_file = requests.put(href, data="Hello Yandex!")
    assert res_upload_file.status_code == 201
    
    # 4. Проверяем, что файл действительно появился
    res_check = requests.get(api_url, headers=headers, params={"path": file_path})
    assert res_check.status_code == 200 and res_check.json().get("type") == "file"
    
    # 5. Удаляем созданную папку со всеми файлами внутри
    res_delete = requests.delete(api_url, headers=headers, params={"path": folder_name})
    assert res_delete.status_code in [202, 204]
