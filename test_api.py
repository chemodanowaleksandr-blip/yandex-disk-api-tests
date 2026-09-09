import pytest
import requests

def pytest_addoption(parser):
    parser.addoption("--token", action="store", default=None, help="Yandex Disk API Token")

@pytest.fixture
def token(request):
    token_value = request.config.getoption("--token")
    if not token_value:
        pytest.fail("Запустите тест командой: pytest test_api.py --token=ТВОЙ_ТОКЕН")
    return token_value

# ТЕСТ 1: Проверка метода GET (Связь с Яндекс Диском)
def test_yandex_disk_connection(token):
    url = "https://yandex.net"
    headers = {"Authorization": f"OAuth {token}"}
    
    response = requests.get(url, headers=headers)
    assert response.status_code == 200

# ТЕСТ 2: Проверка метода POST (Создание папки) и DELETE (Удаление папки)
def test_create_and_delete_folder(token):
    base_url = "https://yandex.net/resources"
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": "Yandex_Stazhirovка_Test_Folder"}
    
    # 1. СОЗДАЕМ ПАПКУ (POST)
    create_response = requests.put(base_url, headers=headers, params=params)
    # Код 201 означает, что папка успешно создана
    assert create_response.status_code == 201
    
    # 2. ПРОВЕРЯЕМ, ЧТО ПАПКА СУЩЕСТВУЕТ (GET)
    check_response = requests.get(base_url, headers=headers, params=params)
    assert check_response.status_code == 200
    assert check_response.json().get("type") == "dir"
    
    # 3. УДАЛЯЕМ ПАПКУ ЗА СОБОЙ (DELETE)
    delete_response = requests.delete(base_url, headers=headers, params=params)
    # Код 202 или 204 означает успешное удаление/принятие запроса
    assert delete_response.status_code in [202, 204]
