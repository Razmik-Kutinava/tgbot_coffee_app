# Настройка RLS политики для таблицы User

## Проблема
RLS (Row Level Security) блокирует INSERT для anon роли, поэтому бот не может создавать пользователей.

## Решение: Создать политику для anon роли

### Шаг 1: Откройте Supabase Dashboard
1. Перейдите в **Authentication** → **Policies**
2. Выберите таблицу **User**
3. Нажмите **Create policy**

### Шаг 2: Создайте политику для INSERT

**Параметры политики:**
- **Policy Name**: `Enable insert for anon users`
- **Table**: `public.User`
- **Policy Behavior**: `PERMISSIVE`
- **Policy Command**: `INSERT`
- **Target Roles**: `anon`
- **WITH CHECK clause**: `true`

### Шаг 3: SQL запрос для создания политики

Выполните в SQL Editor:

```sql
CREATE POLICY "Enable insert for anon users"
ON "public"."User"
AS PERMISSIVE
FOR INSERT
TO anon
WITH CHECK (true);
```

### Шаг 4: Проверка

После создания политики:
1. Перезапустите бота
2. Нажмите на кнопку "📦 Открыть каталог" в боте
3. Проверьте таблицу User в Supabase - должна появиться запись

## Что изменилось в коде:

1. ✅ Убрана передача `id` при INSERT (если это автоинкремент)
2. ✅ Добавлен поиск пользователя по `telegramUsername` (если есть)
3. ✅ Добавлено детальное логирование для отладки
4. ✅ Улучшена обработка ошибок

## Логи для проверки:

После создания политики в логах бота должно появиться:
- `Проверка регистрации пользователя {user_id}`
- `Пользователь {user_id} не найден в БД, создаём новую запись`
- `Создание нового пользователя (telegramId: {user_id}, имя: {name})`
- `✅ Автоматически зарегистрирован пользователь {user_id}`

Если видите ошибки - проверьте логи Supabase Dashboard → Logs.

