-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    first_name TEXT,
    username TEXT,
    email TEXT,
    points INTEGER DEFAULT 0,
    referral_code TEXT,
    location_latitude DOUBLE PRECISION,
    location_longitude DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы заказов
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL,
    order_name TEXT NOT NULL,
    modifiers TEXT[], -- Массив модификаторов
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);

-- Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для автоматического обновления updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

