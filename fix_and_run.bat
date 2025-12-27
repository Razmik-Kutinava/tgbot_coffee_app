@echo off
chcp 65001 >nul
echo Удаление старых версий...
pip uninstall supabase realtime postgrest gotrue -y

echo.
echo Установка совместимых версий...
pip install supabase==2.3.0 realtime==2.3.0 postgrest==0.16.0 gotrue==2.6.0

echo.
echo Проверка импорта...
python -c "from supabase import create_client; print('✅ Supabase работает!')"

echo.
echo Запуск бота...
python bot.py

