import telebot
from cordova import CordovaApp
import zipfile
import os

bot = telebot.TeleBot("7368730334:AAH9xUG8G_Ro8mvV_fDQxd5ddkwjxHnBoeg")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Отправьте .zip файл с вашим проектом.")

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
        
        with open("project_folder/platforms/android/app/build/outputs/apk/debug/app-debug.apk", 'rb') as apk_file:
            bot.send_document(message.chat.id, apk_file)
        
        os.remove("project.zip")
        os.rmdir("project_folder")

bot.polling()
