# Pocketnet Node Monitor

Сервис для мониторинга и сбора метрик узлов сети Pocketnet.

## Описание

Pocketnet Node Monitor - это инструмент для отслеживания состояния узлов сети Pocketnet. Сервис собирает информацию о доступности узлов, их версиях, производительности и других метриках через RPC API.

## Основные возможности

- Автоматическое обнаружение узлов сети
- Сбор метрик узлов (версия, высота блока, количество пиров)
- Мониторинг доступности узлов
- REST API для получения статистики
- Хранение исторических данных
- Географическое распределение узлов

## Требования

- Docker
- Docker Compose
- Доступ к сети Pocketnet

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/pocketnet-node-monitor.git
cd pocketnet-node-monitor
```

2. Настройте конфигурацию в `config/config.yml`:
```yaml
scanner:
  scan_interval: 300  # интервал сканирования в секундах
  timeout: 5         # таймаут подключения
  rpc_port: 8080     # порт RPC API

mongodb:
  uri: mongodb://mongodb:27017
  database: pocketnet_monitor

initial_peers:
  - "seed1.pocketnet.com"
  - "seed2.pocketnet.com"
```

3. Запустите сервис:
```bash
docker-compose up -d
```

## API Endpoints

### Получение списка активных узлов
```http
GET /api/v1/nodes
```

Ответ:
```json
{
  "nodes": [
    {
      "ip": "1.2.3.4",
      "version": "1.0.0",
      "block_height": 12345,
      "peers": 50,
      "last_seen": "2024-03-20T15:30:00Z"
    }
  ]
}
```

### Получение метрик сети
```http
GET /api/v1/metrics
```

Ответ:
```json
{
  "total_nodes": 100,
  "active_nodes": 95,
  "average_block_height": 12345,
  "version_distribution": {
    "1.0.0": 80,
    "0.9.9": 20
  }
}
```

## Мониторинг

Состояние сервиса можно отслеживать через логи:
```bash
docker-compose logs -f node-monitor
```

## Разработка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate     # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите тесты:
```bash
pytest tests/
```

## Структура проекта

```
pocketnet-node-monitor/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/
│   ├── api/
│   │   ├── routes.py
│   │   └── handlers.py
│   ├── services/
│   │   ├── node_scanner.py
│   │   ├── peer_discovery.py
│   │   └── metrics_collector.py
│   ├── models/
│   │   ├── node.py
│   │   └── metrics.py
│   └── database/
│       └── mongodb.py
├── config/
│   └── config.yml
└── requirements.txt
```

## Лицензия

MIT License

## Поддержка

При возникновении проблем создавайте issue в репозитории проекта или обращайтесь к разработчикам:
- Email: support@example.com
- Telegram: @pocketnet_support

## Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функциональности
3. Внесите изменения
4. Отправьте pull request

Пожалуйста, убедитесь, что ваш код соответствует стандартам PEP 8 и покрыт тестами.
