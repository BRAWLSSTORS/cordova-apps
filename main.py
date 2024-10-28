import telebot
import os
import zipfile
from cordova import Cordova  # Assuming 'python-cordova' library

TOKEN = '7368730334:AAH9xUG8G_Ro8mvV_fDQxd5ddkwjxHnBoeg'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Отправьте .zip файл с HTML, CSS, JS файлами для сборки.")

@bot.message_handler(content_types=['document'])
def handle_zip(message):
    file_info = bot.get_file(message.document.file_id)
    if not file_info.file_path.endswith('.zip'):
        bot.send_message(message.chat.id, "Пожалуйста, отправьте файл в формате .zip")
        return

    file_path = bot.download_file(file_info.file_path)
    with open("source.zip", "wb") as f:
        f.write(file_path)

    with zipfile.ZipFile("source.zip", "r") as zip_ref:
        zip_ref.extractall("project")

    # Cordova Build (adjust to your Cordova setup)
    cordova = Cordova(project_path="project")
    cordova.build()  # Here, additional build specifics may be necessary.

    # Send back the output (example .apk/.ipa)
    with open("project/platforms/android/build/outputs/apk/app.apk", "rb") as app_file:
        bot.send_document(message.chat.id, app_file)

    # Clean up
    os.remove("source.zip")
    os.rmdir("project")

bot.polling()
