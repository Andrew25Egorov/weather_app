# 🌦️ Weather App

Веб-приложение на Django для получения прогноза погоды по городам с автодополнением, поддержкой кириллицы и почасовым прогнозом. Используются публичные API: Nominatim и Open-Meteo.

## 🚀 Возможности

- Поиск города с автозаполнением (autocomplete)
- Отображение текущей и почасовой погоды на 12 часов вперёд
- Поддержка кириллицы и других языков
- Кеширование координат и прогнозов
- Поддержка направления ветра (в градусах и компасных точках)
- Современный дизайн с Tailwind CSS

## 🛠️ Установка и запуск

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/Andrew25Egorov/weather-app.git
cd weather-app
```

### 2. Создайте и активируйте виртуальное окружение
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

### 4. Запустите сервер
```bash
python manage.py runserver
```

Приложение будет доступно по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 🧪 Тесты
Для запуска тестов:
```bash
python manage.py test
```

## 🗺️ Используемые API
- [Open-Meteo](https://open-meteo.com/) — погодные данные
- [Nominatim (OpenStreetMap)](https://nominatim.openstreetmap.org/) — геокодирование городов

## 📁 Структура
```
weather/
├── views.py                # Логика представлений
├── templates/weather/      # HTML-шаблоны
├── static/                 # Статика (если Tailwind установлен локально)
├── templatetags/           # Фильтры (напр. направление ветра)
├── constants.py            # Настройки API и описания погоды
├── tests.py                # Тесты приложения
```

## 💡 Пример запроса
```
Город: Санкт-Петербург, Россия
→ Температура: 18°C
→ Ветер: 5 м/с, Ю-З
→ Прогноз на 12 часов вперед
```

## 📦 Зависимости (из requirements.txt)
```
Django>=3.2
requests
```

## 📄 Лицензия
Проект открыт под лицензией MIT.

---

Made with ❤️ by Andrew Egorov
