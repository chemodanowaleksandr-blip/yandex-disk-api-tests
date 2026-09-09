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
    url = "https://yandex.net"
    f_path = "Yandex_Stazhirovka_Test_Folder"
    file_path = f"{f_path}/test_file.txt"
    
    assert requests.put(url, headers=h, params={"path": f_path}).status_code == 201
    
    upload_url = "https://yandex.net/resources/upload"
    upload_res = requests.get(upload_url, headers=h, params={"path": file_path, "overwrite": "true"})
    assert upload_res.status_code == 200
    href = upload_res.json().get("href")
    
    assert requests.put(href, data=b"Hello Yandex!").status_code == 201
    
    check_res = requests.get(url, headers=h, params={"path": file_path})
    assert check_res.status_code == 200 and check_res.json().get("type") == "file"
    
    assert requests.delete(url, headers=h, params={"path": f_path}).status_code in [202, 204]
