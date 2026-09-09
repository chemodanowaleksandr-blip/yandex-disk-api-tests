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
    
    # Проверяем, что сервер вернул успешный статус-код 200
    assert response.status_code == 200
