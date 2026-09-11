import os
import pytest
import requests

# Базовый URL вынесен в константу, чтобы не дублировать его в тестах
BASE_URL = "https://yandex.net"


@pytest.fixture
def token():
    """Фикстура для получения OAuth-токена."""
    # Пытается взять токен из секретов GitHub Actions, если его там нет — берет дефолтное значение
    return os.getenv("YANDEX_TOKEN", "ВАШ_РЕАЛЬНЫЙ_ТОКЕН")


@pytest.fixture
def headers(token):
    """Фикстура для формирования заголовков авторизации."""
    return {"Authorization": f"OAuth {token}"}


def test_yandex_disk_connection(headers):
    """Проверка доступности API Яндекс Диска."""
    res = requests.get(BASE_URL, headers=headers)
    assert res.status_code == 200


def test_yandex_disk_full_lifecycle(headers):
    """Полный жизненный цикл: создание папки, получение ссылки, загрузка файла, проверка и удаление."""
    resources_url = f"{BASE_URL}/resources"
    upload_url = f"{BASE_URL}/resources/upload"
    
    _path = "yandex_stazhirovka_test_folder"
    file_path = f"{_path}/test_file.txt"
    
    # 1. Создание папки (201 — создано, 409 — папка уже существует, если прошлый тест упал)
    res_mkdir = requests.put(resources_url, headers=headers, params={"path": _path})
    assert res_mkdir.status_code in (201, 409)

    # 2. Получение ссылки для загрузки файла
    res_upload_link = requests.get(
        upload_url, 
        headers=headers, 
        params={"path": file_path, "overwrite": "true"}
    )
    assert res_upload_link.status_code == 200
    href = res_upload_link.json().get("href")
    assert href is not None

    # 3. Загрузка файла по полученной ссылке
    res_upload_file = requests.put(href, data="Hello Yandex!")
    assert res_upload_file.status_code == 201

    # 4. Проверка, что файл действительно появился на Диске
    res_check = requests.get(resources_url, headers=headers, params={"path": file_path})
    assert res_check.status_code == 200
    assert res_check.json().get("type") == "file"

    # 5. Удаление созданной папки со всем содержимым (202 — принято на удаление, 204 — удалено)
    res_delete = requests.delete(resources_url, headers=headers, params={"path": _path})
    assert res_delete.status_code in (202, 204)
