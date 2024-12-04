import re
from typing import Optional

def ExtractVersion(value: Optional[str] = None):
    if value is None:
        raise ValueError("value не может быть None")
    
    match = re.search(r'/Satoshi:([^/]+)/', value)

    if match:
        return match.group(1)
    
    return value

    
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