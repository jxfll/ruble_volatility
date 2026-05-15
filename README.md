# Трекер волатильности рубля (Ruble Volatility Tracker)

Веб-приложение для мониторинга, анализа и визуализации волатильности курса российского рубля (RUB). Построено на стеке Python (Django), JavaScript и Docker.

## 🛠️ Технологический стек

* **Бэкенд:** Python, Poetry, Django, Postgres, Docker, Docker Compose, GitHub Actions
* **Фронтенд:** HTML, CSS, JavaScript, Chart.js, NPM
## 📦 Структура проекта

```text
├── .github/workflows/   # Сценарии автотестов и деплоя (CI/CD)
├── analytics/           # Модули расчета волатильности и логика данных
├── core/                # Главное приложение и настройки Django
├── data/                # Хранение локальных баз данных / файлов данных
├── static/              # Фронтенд-ресурсы (скрипты, стили, изображения)
├── check_system.py      # Скрипт проверки готовности системы и окружения
├── docker-compose.yaml  # Конфигурация Docker-контейнеров
├── Dockerfile           # Инструкции сборки Docker-образа
└── pyproject.toml       # Зависимости и пакеты Poetry
```

## ⚙️ Установка и запуск

### Требования
Перед началом работы убедитесь, что у вас установлены:
* [Docker и Docker Compose](https://docker.com)
* [Python 3.10+](https://python.orgdownloads/)
* [Poetry](https://python-poetry.orgdocs/#installation)

### Локальный запуск (Без Docker)

1. Склонируйте репозиторий:
   ```bash
   git clone github.com/jxfll/ruble_volatility
   cd ruble_volatility
   ```

2. Установите зависимости через Poetry:
   ```bash
   poetry install
   ```

3. Запустите проверку конфигурации:
   ```bash
   poetry run python check_system.py
   ```

4. Примените миграции базы данных:
   ```bash
   poetry run python manage.py migrate
   ```

5. Запустите сервер разработки:
   ```bash
   poetry run python manage.py runserver
   ```

### Быстрый запуск через Docker

Чтобы автоматически собрать и запустить проект в контейнерах, выполните:

```bash
docker-compose up --build
```
После сборки приложение будет доступно по адресу `http://localhost:8000` (или по порту, указанному в настройках).

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).
