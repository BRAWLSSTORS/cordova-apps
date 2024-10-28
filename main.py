import telebot
import os
import zipfile
import subprocess
from cordova import CordovaApp

bot = telebot.TeleBot("YOUR_TOKEN")

def install_cordova():
    try:
        subprocess.check_call(["pip", "install", "git+https://github.com/talpor/python-cordova.git"])
    except subprocess.CalledProcessError:
        return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    if install_cordova():
        bot.send_message(message.chat.id, "Библиотека python-cordova установлена. Теперь отправьте .zip файл с вашим проектом.")
    else:
        bot.send_message(message.chat.id, "Не удалось установить библиотеку python-cordova.")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.mime_type == 'application/zip':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("project.zip", 'wb') as new_file:
            new_file.write(downloaded_file)
        
        with zipfile.ZipFile("project.zip", 'r') as zip_ref:
            zip_ref.extractall("project_folder")
        
        app = CordovaApp("project_folder")
        app.build('android')
        
        apk_path = "project_folder/platforms/android/app/build/outputs/apk/debug/app-debug.apk"
        if os.path.exists(apk_path):
            with open(apk_path, 'rb') as apk_file:
                bot.send_document(message.chat.id, apk_file)
        else:
            bot.send_message(message.chat.id, "Ошибка сборки приложения.")
        
        os.remove("project.zip")
        os.rmdir("project_folder")

bot.polling()
