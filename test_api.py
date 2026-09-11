import os
import pytest
import requests

# Базовый URL для Yandex Cloud API (REST API Диска)
BASE_URL = "https://yandex.net"


@pytest.fixture
def token():
    # Токен уже встроен напрямую в код, как вы и просили
    return "y0__wgBEKXYpokBGNuWAyCC8PD8GDDZz872B2Flus-8dUYZRjhCK6CgmhfJ62h9"


@pytest.fixture
def headers(token):
    return {"Authorization": f"OAuth {token}"}


def test_yandex_disk_connection(headers):
    """Проверка доступности самого Диска (получение метаданных)"""
    res = requests.get(BASE_URL, headers=headers)
    assert res.status_code == 200
    assert "total_space" in res.json()


def test_yandex_disk_full_lifecycle(headers):
    """Сквозной тест: создание папки -> загрузка файла -> проверка -> удаление"""
    resources_url = f"{BASE_URL}/resources"
    upload_url = f"{BASE_URL}/resources/upload"

    folder_name = "yandex_stazhirovka_test_folder"
    file_path = f"{folder_name}/test_file.txt"

    # 1. Создание папки
    res_mkdir = requests.put(
        resources_url, headers=headers, params={"path": folder_name}
    )
    assert res_mkdir.status_code in (201, 409)

    # 2. Получение ссылки для загрузки
    res_upload_link = requests.get(
        upload_url,
        headers=headers,
        params={"path": file_path, "overwrite": "true"},
    )
    assert res_upload_link.status_code == 200
    href = res_upload_link.json().get("href")
    assert href is not None

    # 3. Загрузка контента по полученной ссылке
    res_upload_file = requests.put(href, data="Hello Yandex!")
    assert res_upload_file.status_code == 201

    # 4. Проверка существования файла в метаданных
    res_check = requests.get(
        resources_url, headers=headers, params={"path": file_path}
    )
    assert res_check.status_code == 200
    assert res_check.json().get("type") == "file"
    assert res_check.json().get("name") == "test_file.txt"

    # 5. Очистка: удаление созданной папки мимо корзины (permanently=true)
    res_delete = requests.delete(
        resources_url,
        headers=headers,
        params={"path": folder_name, "permanently": "true"},
    )
    assert res_delete.status_code in (202, 204)
