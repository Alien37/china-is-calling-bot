@echo off
cd /d D:\telegram_bot
call D:\telegram_bot\bot_env\Scripts\activate
python bot.py >> D:\telegram_bot\bot.log 2>&1
