# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2026
# Coded by AnonimNEO (Github)

# Работа с процессами
import win32process
import win32gui
import psutil
# Логирование
from loguru import logger
# Работа с файлами
import os
import re
# Паузы сканирования
import time
# Работа с реестром
import winreg

auh_version = "0.5.4 Beta"

DEBUG_MODE = False

NET_PATH = r"C:\Users\Adminus\AppData\Local\Temp\.net"
NH_PATH = r"C:\Users\Adminus\AppData\Local\NHelperV4"
NH_DIRS = [r"C:\Users\Adminus\AppData\Local\NHelperV3.4", r"C:\Users\Adminus\AppData\Local\NHelperV4", r"C:\Users\Adminus\AppData\Local\NHelperV4.1", r"C:\Users\Adminus\AppData\Local\NHelperV4.2"]

def kill_process_by_name(process_name):
    # Проходим по всем запущенным процессам
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if process_name.lower() in proc.info["name"].lower():
                try:
                    p = psutil.Process(proc.info["pid"])
                    exe_file = p.exe()
                    p.kill()
                    p.wait()
                    logger.info(f"AN - Процесс с именем {proc.info["name"]} (PID:{proc.info["pid"]}) - убит.")
                except:
                    logger.exception(f"AN - Ошибка при закрытии процесса с именем {proc.info["name"]} (PID:{proc.info["pid"]})")

                try:
                    os.remove(exe_file)
                    logger.info(f"AN - Файл процесса с именем {proc.info["name"]} - удалён.")
                except:
                    logger.exception(f"AUH - Ошибка при удалении исполняемого файла процесса с именем {proc.info["name"]} (PID:{proc.info["pid"]})")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        except:
            logger.exception(f"AUH - Ошибка при закрытии процесса по имени {proc.info["name"]} (PID:{proc.info["pid"]})")



def kill_some_process_by_name(process_name_list):
    """Убиваем все процессы с переданым именем"""
    for process_name in process_name_list:
        kill_process_by_name(process_name)



def get_folder_names(target_path):
    try:
        # Проверяем, существует ли указанный путь
        if os.path.exists(target_path):
            # Получаем список всех объектов и фильтруем только папки
            folders = [name for name in os.listdir(target_path) if os.path.isdir(os.path.join(target_path, name))]
            return folders
        else:
            return 0
    except:
        logger.exception(f"AUH - неизвестная ошибка при переборе каталогов")
        return 0



def break_xml():
    """Повреждение xml файла интерфейса настроек"""
    for root, dirs, files in os.walk(NH_PATH):
        if "user.config" in files:
            file_path = os.path.join(root, "user.config")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r'^<\?xml[^?]*\?>', '<?xml version="1.0" encoding="utf-0"?>', content)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
    logger.success("AUH - XML файл повреждён")



def block_defend():
    """Создание параметра EnableBlockSearch (DWORD) по пути HKEY_LOCAL_MACHINE/SOFTWARE/Mozaila/"""
    k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Mozilla", 0, winreg.KEY_WRITE)
    winreg.SetValueEx(k, "EnableBlockSearch", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(k)
    logger.success("AUH - Ложная защита nhelper включена")



def kill_nh(DEBUG_MODE=False):
    """Нахождение имени процесса, затем его убийство и удаление исполняемого файла"""
    folder_list = get_folder_names(NET_PATH)

    if isinstance(folder_list, list):
        kill_some_process_by_name(folder_list)
        for i in folder_list:
            try:
                os.remove(f"{NET_PATH}\\{folder_list[i]}")
                logger.success(f"AUH - Каталог {NET_PATH}\\{folder_list[i]} удалён.")
            except:
                if DEBUG_MODE:
                    logger.error(f"AUH - ошибка при удалении подкаталога в {NET_PATH}")
                pass

    for dir in NH_DIRS:
        try:
            os.remove(dir)
        except:
            pass



def get_windows_titles(DEBUG_MODE=False):
    """Получаем заголовки окон"""
    window_list = []

    def enum_windows_callback(hwnd, context):
        # Проверяем, видимо ли окно
        if win32gui.IsWindowVisible(hwnd):
            # Получаем заголовок окна
            title = win32gui.GetWindowText(hwnd)

            try:
                thread_id, pid = win32process.GetWindowThreadProcessId(hwnd)
            except:
                logger.exception(f"AUH - Ошибка при получении PID для окна {title}")
                return # Продолжаем перебор окон

            window_list.append((title, pid))

    # Запускаем перебор всех окон
    win32gui.EnumWindows(enum_windows_callback, None)
    if DEBUG_MODE:
        logger.debug(window_list)
    return window_list



def kill_bad_window(DEBUG_MODE=False):
    bad_title_list = ["подтверждение", "удаления", "(не отвечает)", "процессов", "wanlocker", "разблокировка",
                      "ограничений", "управление", "автозагрузкой", "fllitz", "defender", "готово", "редактор",
                      "редактирование", "значения", "файловый", "менеджер", "среда", "восстановления", "успех",
                      "тригеры", "информация", "ошибка", "диспетчер", "задач", "описание", "process", "параметры",
                      "root", "guard", ".net", "unlocker", "system", "ultra", "unlcoker", "pirate", "helper",
                      "создатели", ":3", "[главное]", "анализ", "запретов", "восстановление", "ассоциаций",
                      "очистка", "музыка", "выход", "erocs", "[main]", "recovery", "kit", "vortex"]

    windows = get_windows_titles(DEBUG_MODE)

    for title, pid in windows:
        title_lower = title.lower()
        if DEBUG_MODE:
            logger.debug(f"AUH - PID:{pid} - {title}")
        for bad_title in bad_title_list:
            if bad_title in title_lower:
                logger.info(f"AUH - Обнаружен заголовок {title}, закрытие процесса (pid: {pid})...")

                try:
                    p = psutil.Process(pid)
                    p_name = p.name()
                    exe_file = p.exe()
                    p.kill()
                    p.wait()
                    logger.success(f"AUH - Процесс {p_name} (PID: {pid}) успешно убит.")

                    try:
                        if os.path.exists(exe_file):
                            os.remove(exe_file)
                            logger.info(f"AUH - Файл процесса {p_name} успешно удален: {exe_file}")
                    except:
                        logger.exception(f"AUH - Ошибка при удалении файла процесса {p_name} (PID: {pid})")

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    logger.error(f"AUH - Не удалось получить доступ к процессу с PID {pid}")
                except:
                    logger.error(f"AUH - Ошибка при обработке процесса с PID {pid}")
                break



if __name__ == "__main__":
    try:
        logger.info(f">>> Запуск AntiUnclokerHelper v{auh_version}...")
        logger.info(">>> Настройка логирования...")
        try:
            logger.add(f"AN_log.txt", format="{time} {level} {message}", rotation="10 MB", compression="zip")
            from elevate import elevate
            elevate()
            global user_name
            user_name = os.getlogin()
            logger.success("AUH - Успешная подготовка к работе, запуск...")
        except:
            logger.exception("AUH - Ошибка инициализации")
        logger.success("AUH - Успешный запуск")
        while True:
            print("\n" + "=" * 47)
            print("║" + " " * 45 + "║")
            print("║" + "  Для какой программы работаем?".center(45) + "║")
            print("║" + " " * 45 + "║")
            print("║" + "  0) Выход из утилиты".ljust(45) + "║")
            print("║" + "  1) Универсальные методы".ljust(45) + "║")
            print("║" + "  2) NHelper".ljust(45) + "║")
            print("║" + "  3) Recovery Kit".ljust(45) + "║")
            print("║" + " " * 45 + "║")
            print("=" * 47)
            program = int(input(">>> Ваш выбор: ").strip())
            if program == 0:
                logger.info("AUH - Выход...")
                exit()
            elif program == 1:
                if input("\n[?] Включить цикл? (1 - да, другое - нет): ").strip() == "1":
                    while True:
                        try:
                            kill_bad_window(DEBUG_MODE)
                            logger.info("AUH - Цикл title завершён, повтор...")
                            time.sleep(0.5)
                        except KeyboardInterrupt:
                            logger.warning("AUH - Цикл остановлен пользователем")
                            break
                else:
                    kill_bad_window(DEBUG_MODE)
            elif program == 2:
                while True:
                    print("\n" + "=" * 47)
                    print("║" + " " * 45 + "║")
                    print("║" + "  Какой уязвимостью хотите воспользоваться?".center(45) + "║")
                    print("║" + " " * 45 + "║")
                    print("║" + "  0) Выход в меню".ljust(45) + "║")
                    print("║" + "  1) Названием процесса в %Temp%/.net/".ljust(45) + "║")
                    print("║" + "  2) Защита NHelper от getgans".ljust(45) + "║")
                    print("║" + "  3) Смена кодировки XML в user.config".ljust(45) + "║")
                    print("║" + " " * 45 + "║")
                    print("=" * 47)

                    choice = int(input("\n>>> Ваш выбор: ").strip())

                    if choice == 0:
                        break
                    elif choice == 1:
                        if input("\n[?] Включить цикл? (1 - да, другое - нет): ").strip() == "1":
                            while True:
                                try:
                                    kill_nh(DEBUG_MODE)
                                    logger.info("AUH - Цикл nh завершён, повтор...")
                                    time.sleep(0.5)
                                except KeyboardInterrupt:
                                    logger.warning("AUH - Цикл остановлен пользователем")
                                    break
                        else:
                            kill_nh(DEBUG_MODE)
                    elif choice == 2:
                        logger.info("AUH - Применение защиты NHelper...")
                        block_defend()
                    elif choice == 3:
                        logger.info("AUH - Изменение кодировки XML...")
                        break_xml()
                    else:
                        print("\n[!] Неправильный ввод. Попробуйте ещё раз.")
            elif program == 3:
                print('>>> Для RecoveryKit на данный момент нет уникальных уязвимостей, на него работает раздел "Универсальные"')
            else:
                print("\n[!] Неправильный ввод. Попробуйте ещё раз.")
    except:
        logger.exception("AUH - Неизвестная ошибка")
