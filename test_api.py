import os
import pytest
import requests

@pytest.fixture
def token():
    return os.getenv("YANDEX_TOKEN")

def test_yandex_disk_connection(token):
    target_url = "https://yandex.net"
    res = requests.get(target_url, headers={"Authorization": f"OAuth {token}"})
    assert res.status_code == 200

def test_yandex_disk_full_lifecycle(token):
    headers_dict = {"Authorization": f"OAuth {token}"}
    final_api_url = "https://yandex.netresources"
    
    fn = "Yandex_Stazhirovka_Test_Folder"
    fp = f"{fn}/test_file.txt"
    
    # 1. Создаем папку
    res_mkdir = requests.put(final_api_url, headers=headers_dict, params={"path": fn})
    assert res_mkdir.status_code in [201, 409]
    
    # 2. Получаем ссылку для загрузки файла
    upload_endpoint = "https://yandex.netresources/upload"
    res_upload_link = requests.get(upload_endpoint, headers=headers_dict, params={"path": fp, "overwrite": "true"})
    assert res_upload_link.status_code == 200
    href = res_upload_link.json().get("href")
    
    # 3. Загружаем сам файл по полученной ссылке
    res_upload_file = requests.put(href, data="Hello Yandex!")
    assert res_upload_file.status_code == 201
    
    # 4. Проверяем, что файл действительно появился
    res_check = requests.get(final_api_url, headers=headers_dict, params={"path": fp})
    assert res_check.status_code == 200 and res_check.json().get("type") == "file"
    
    # 5. Удаляем созданную папку со всеми файлами внутри
    res_delete = requests.delete(final_api_url, headers=headers_dict, params={"path": fn})
    assert res_delete.status_code in [202, 204]
