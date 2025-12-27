# tgbot_coffee_app

Telegram бот для заказа кофе с интеграцией мини-приложения Flutter и Supabase.

## Описание

Бот позволяет пользователям:
- Выбирать кофейню
- Просматривать меню
- Делать заказы
- Отслеживать историю заказов

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Razmik-Kutinava/tgbot_coffee_app.git
cd tgbot_coffee_app
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения:
- Создайте файл `.env` на основе `env_example.txt`
- Добавьте токен бота, ключи Supabase и другие необходимые параметры

## Запуск

```bash
python bot.py
```

## Структура проекта

- `bot.py` - основной файл бота
- `requirements.txt` - зависимости Python
- `prisma/schema.prisma` - схема базы данных
- `supabase_schema.sql` - SQL схема для Supabase

## Интеграции

- **Telegram Bot API** - для взаимодействия с пользователями
- **Supabase** - база данных и backend
- **Flutter WebApp** - мини-приложение для заказов

## Документация

Дополнительная документация находится в файлах:
- `SUPABASE_SETUP.md` - настройка Supabase
- `WEBAPP_INTEGRATION.md` - интеграция с WebApp
- `RLS_POLICY_SETUP.md` - настройка политик безопасности
