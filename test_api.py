import pytest
import requests
import config

BASE_URL = "https://yandex.net"


@pytest.fixture
def token():
    """Фикстура получает токен из отдельного файла конфигурации."""
    return config.YANDEX_TOKEN


@pytest.fixture
def headers(token):
    return {
        "Authorization": f"OAuth {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }


def test_yandex_disk_connection(headers):
    res = requests.get(BASE_URL, headers=headers)
    assert res.status_code == 200


def test_yandex_disk_full_lifecycle(headers):
    resources_url = f"{BASE_URL}/resources"
    upload_url = f"{BASE_URL}/resources/upload"
    
    _path = "disk:/yandex_test_folder_99"
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
    
    try:
        href = res_upload_link.json().get("href")
    except requests.exceptions.JSONDecodeError:
        pytest.fail(f"Yandex returned non-JSON response. Text: {res_upload_link.text[:200]}")
        
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
    assert res_delete.status_code in (202, 204, 404)
