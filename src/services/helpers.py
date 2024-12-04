import re
from typing import Optional

# -----------------------------------------------------------------------------------------------
def ExtractVersion(value: Optional[str] = None):
    if value is None:
        raise ValueError("value не может быть None")
    
    match = re.search(r'/Satoshi:([^/]+)/', value)

    if match:
        return match.group(1)
    
    return value

# -----------------------------------------------------------------------------------------------
def ExtractIPAddress(value: Optional[str] = None) -> str:
    if value is None:
        raise ValueError("value не может быть None")
    
    # Регулярное выражение для поиска IPv4 и IPv6 адресов
    ip_pattern = r'(?:(?:\d{1,3}\.){3}\d{1,3}|[0-9a-fA-F]{1,4}(:[0-9a-fA-F]{1,4}){7})'
    
    # Поиск первого совпадения
    match = re.search(ip_pattern, value)
    
    if match:
        return match.group(0)
    
    return value

# -----------------------------------------------------------------------------------------------
# Настройка логирования
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------------
# Загрузка конфигурации
import yaml
import sys
def load_config():
    config_file = 'config/config.yml'  # По умолчанию используем основной файл конфигурации
    if '--dev' in sys.argv:  # Проверяем, передан ли аргумент --dev
        config_file = 'config/config_dev.yml'  # Если да, используем dev файл конфигурации
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)
config = load_config()