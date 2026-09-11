import os
import pytest
import requests

BASE_URL = "https://yandex.net"


@pytest.fixture
def token():
    # REPLACE YOUR_ACTUAL_TOKEN WITH YOUR REAL OAUTH TOKEN
    return "YOUR_ACTUAL_TOKEN"


@pytest.fixture
def headers(token):
    return {"Authorization": f"OAuth {token}"}


def test_yandex_disk_connection(headers):
    res = requests.get(BASE_URL, headers=headers)
    assert res.status_code == 200


def test_yandex_disk_full_lifecycle(headers):
    resources_url = f"{BASE_URL}/resources"
    upload_url = f"{BASE_URL}/resources/upload"
    
    _path = "yandex_stazhirovka_test_folder"
    file_path = f"{_path}/test_file.txt"
    
    # 1. Create folder
    res_mkdir = requests.put(resources_url, headers=headers, params={"path": _path})
    assert res_mkdir.status_code in (201, 409)

    # 2. Get upload link
    res_upload_link = requests.get(
        upload_url, 
        headers=headers, 
        params={"path": file_path, "overwrite": "true"}
    )
    assert res_upload_link.status_code == 200
    href = res_upload_link.json().get("href")
    assert href is not None

    # 3. Upload file
    res_upload_file = requests.put(href, data="Hello Yandex!")
    assert res_upload_file.status_code == 201

    # 4. Check file exists
    res_check = requests.get(resources_url, headers=headers, params={"path": file_path})
    assert res_check.status_code == 200
    assert res_check.json().get("type") == "file"

    # 5. Delete folder
    res_delete = requests.delete(resources_url, headers=headers, params={"path": _path})
    assert res_delete.status_code in (202, 204)
