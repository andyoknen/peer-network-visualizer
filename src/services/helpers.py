import re
from typing import Optional

# -----------------------------------------------------------------------------------------------
def ExtractVersion(value: Optional[str] = None):
    if value is None:
        return ""
    
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
# Загрузка конфигурации
import yaml
import sys
def load_config():
    config_file = 'config/config.dev.yml' if '--dev' in sys.argv else 'config/config.yml'
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)
config = load_config()

# -----------------------------------------------------------------------------------------------
# Настройка логирования
import logging

log_level = config.get('logging', {}).get('level', 'ERROR').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/app.log'
)
log = logging.getLogger(__name__)
