import os
import subprocess
import zipfile
import telebot
from telebot import types

# Токен вашего Telegram-бота (замените на ваш токен)п
TOKEN = '7368730334:AAH9xUG8G_Ro8mvV_fDQxd5ddkwjxHnBoeg'

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Декоратор для смены рабочей директории на директорию проекта
def chdir_context(func):
    def wrapped(*args, **kwargs):
        self = args[0]
        cwd = os.getcwd()
        os.chdir(self.path)
        ret = func(*args, **kwargs)
        os.chdir(cwd)
        return ret
    return wrapped

# Применение декоратора ко всем методам класса
def for_all_methods(decorator):
    def decorate(cls):
        for attr, val in cls.__dict__.items():
            if callable(val) and not attr.startswith("__"):
                setattr(cls, attr, decorator(val))
        return cls
    return decorate

# Класс для взаимодействия с Cordova CLI
@for_all_methods(chdir_context)
class App:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def build(self, platform, release=False):
        cmd_params = ['cordova', 'build', platform]
        if release:
            cmd_params.append('--release')
        return subprocess.call(cmd_params) == 0

    def archive(self, platform):
        os.chdir('platforms')
        archive_name = f'{self.name}-{platform}.zip'
        return subprocess.call(['tar', '-czf', archive_name, platform]) == 0

    def prepare(self, platform):
        return subprocess.call(['cordova', 'prepare', platform]) == 0

    def compile(self, platform):
        return subprocess.call(['cordova', 'compile', platform]) == 0

# Функция для обработки и распаковки загруженного zip-файла
def handle_zip_file(file_path, extract_to):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to

# Команда /start — приветствие и запрос zip-файла
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'Привет! Пришлите zip-файл с HTML, CSS и JavaScript.')

# Обработка документов (загрузка zip-файла)
@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохраняем загруженный файл
    zip_path = f"{message.document.file_name}"
    with open(zip_path, 'wb') as f:
        f.write(downloaded_file)

    # Распаковываем содержимое
    extract_path = f"./{message.document.file_name}_extracted"
    handle_zip_file(zip_path, extract_path)

    # Инициализация Cordova приложения
    app = App(name="MyCordovaApp", path=extract_path)

    # Выполняем команды Cordova
    if app.prepare('android'):
        bot.send_message(message.chat.id, 'Проект подготовлен для Android.')
    if app.build('android'):
        bot.send_message(message.chat.id, 'Сборка завершена успешно.')
    if app.archive('android'):
        bot.send_message(message.chat.id, 'Проект заархивирован.')

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
