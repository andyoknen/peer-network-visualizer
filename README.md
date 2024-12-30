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
- MongoDB
- Доступ к сети Pocketnet

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/andyoknen/peer-network-visualizer.git
cd pocketnet-node-monitor
```

2. Настройте конфигурацию в `config/config.yml`:
```yaml
fastapi:
  host: 0.0.0.0
  port: 5000

scanner:
  scan_interval: 300  # интервал сканирования в секундах
  timeout: 5         # таймаут подключения
  rpc_port: 38081     # порт RPC API

mongodb:
  uri: mongodb://mongodb:27017
  database: pocketnet_monitor

initial_peers:
  - "1.pocketnet.app"
  - "2.pocketnet.app"
  - "3.pocketnet.app"
```

3. Сборка и запуск контейнера:
```bash
docker build -t peer-network-visualizer .
docker run -d --name peer-network-visualizer peer-network-visualizer
```

## API Endpoints

### Получение списка активных узлов
```http
GET /list_nodes
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

### HTML страница
```http
GET /
```

### HTML страница списка узлов
```http
GET /nodes
```

### HTML страница визуальной карты
```http
GET /cloud
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

## Структура проекта

```
pocketnet-node-monitor/
├── docker/
│   ├── dockerfile
│   └── docker-compose.yml
├── config/
│   └── config.yml
├── src/
│   ├── api/
│   │   ├── routes.py
│   ├── services/
│   │   ├── peer_discovery.py
│   │   └── helpers.py
│   └── models/
│       ├── node.py
│       └── peer.py
└── requirements.txt
```

## Лицензия

[Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0)

## Поддержка

При возникновении проблем создавайте issue в репозитории проекта или обращайтесь к разработчикам:
- Email: core@pocketnet.app

## Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функциональности
3. Внесите изменения
4. Отправьте pull request

