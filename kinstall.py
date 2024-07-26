import subprocess
import sys
from termcolor import colored
import distro
import re
import requests

arch_based_distros = [
    "Arch Linux", "Manjaro", "ArcoLinux", "Artix Linux", "EndeavourOS", 
    "Garuda Linux", "BlackArch", "ArchLabs", "Archman", "RebornOS",
    "Bluestar Linux", "Chakra", "Parabola", "Hyperbola"
]

messages = {
    "en": {
        "not_arch": "This script can only be run on an Arch-based Linux distribution.",
        "installing": "Installing",
        "removing": "Removing",
        "searching": "Searching for",
        "package_not_found": "Package not found in pacman or AUR.",
        "error": "An error occurred",
        "select_package": "Please select a package from the list:",
        "invalid_selection": "Invalid selection. Please try again.",
        "invalid_input": "Invalid input. Exiting.",
        "manjaro_warning": "You are using Manjaro. This script might cause issues on Manjaro.",
        "up_to_date": "You are using the latest version.",
        "outdated_version": "Your version is outdated and cannot be used. Please update to the latest version.",
    },
    "pl": {
        "not_arch": "Ten skrypt można uruchomić tylko na dystrybucji Linuksa opartej na Arch.",
        "installing": "Instalowanie",
        "removing": "Usuwanie",
        "searching": "Wyszukiwanie",
        "package_not_found": "Pakiet nie znaleziony w pacman lub AUR.",
        "error": "Wystąpił błąd",
        "select_package": "Proszę wybrać pakiet z listy:",
        "invalid_selection": "Niepoprawny wybór. Proszę spróbować ponownie.",
        "invalid_input": "Niepoprawne dane wejściowe. Zamykanie.",
        "manjaro_warning": "Używasz Manjaro. Ten skrypt może powodować problemy na Manjaro.",
    },
    "ru": {
        "not_arch": "Этот скрипт можно запускать только в дистрибутивах Linux, основанных на Arch.",
        "installing": "Установка",
        "removing": "Удаление",
        "searching": "Поиск",
        "package_not_found": "Пакет не найден в pacman или AUR.",
        "error": "Произошла ошибка",
        "select_package": "Пожалуйста, выберите пакет из списка:",
        "invalid_selection": "Неверный выбор. Пожалуйста, попробуйте снова.",
        "invalid_input": "Неверный ввод. Выход.",
        "manjaro_warning": "Вы используете Manjaro. Этот скрипт может вызвать проблемы на Manjaro.",
    },
    "uk": {
        "not_arch": "Цей скрипт можна запускати лише на дистрибутивах Linux, що базуються на Arch.",
        "installing": "Встановлення",
        "removing": "Видалення",
        "searching": "Пошук",
        "package_not_found": "Пакет не знайдено у pacman або AUR.",
        "error": "Сталася помилка",
        "select_package": "Будь ласка, виберіть пакет зі списку:",
        "invalid_selection": "Невірний вибір. Будь ласка, спробуйте ще раз.",
        "invalid_input": "Неправильний ввід. Вихід.",
        "manjaro_warning": "Ви використовуєте Manjaro. Цей скрипт може викликати проблеми на Manjaro.",
    },
    "de": {
        "not_arch": "Dieses Skript kann nur auf einer Arch-basierten Linux-Distribution ausgeführt werden.",
        "installing": "Installieren",
        "removing": "Entfernen",
        "searching": "Suche nach",
        "package_not_found": "Paket nicht in pacman oder AUR gefunden.",
        "error": "Ein Fehler ist aufgetreten",
        "select_package": "Bitte wählen Sie ein Paket aus der Liste aus:",
        "invalid_selection": "Ungültige Auswahl. Bitte versuchen Sie es erneut.",
        "invalid_input": "Ungültige Eingabe. Beenden.",
        "manjaro_warning": "Sie verwenden Manjaro. Dieses Skript kann auf Manjaro Probleme verursachen.",
    }
}

def get_message(lang, key):
    return messages.get(lang, messages["pl"]).get(key)

def check_arch_based():
    dist = distro.name()
    return dist in arch_based_distros

def version_compare(v1, v2):
    v1_parts = list(map(int, v1.split('.')))
    v2_parts = list(map(int, v2.split('.')))
    
    # Pad the shorter version with zeroes
    while len(v1_parts) < len(v2_parts):
        v1_parts.append(0)
    while len(v2_parts) < len(v1_parts):
        v2_parts.append(0)
    
    return (v1_parts > v2_parts) - (v1_parts < v2_parts)

def run_command(command, timeout=60):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        stdout = result.stdout.decode('utf-8').strip()
        stderr = result.stderr.decode('utf-8').strip()
        return stdout, stderr
    except subprocess.TimeoutExpired:
        return "", "Command timed out"
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.decode('utf-8').strip()
        stderr = e.stderr.decode('utf-8').strip()
        return stdout, stderr

def search_and_select_package(package, lang):
    print(colored(f"{get_message(lang, 'searching')} {package} in AUR...", 'yellow'))
    stdout, stderr = run_command(f"yay -Ss {package}", timeout=120)
    if stderr:
        print(colored(stderr, 'red'))
        print(colored(get_message(lang, "package_not_found"), 'red'))
        return None

    results = stdout.split('\n')
    package_lines = [line for line in results if re.match(r'^\S+', line)]
    if not package_lines:
        print(colored(get_message(lang, "package_not_found"), 'red'))
        return None

    print("\n" + "\n".join(f"{i + 1}. {line.split()[0]} - {line[1:].split(' ', 1)[1] if len(line.split()) > 1 else ''}" for i, line in enumerate(package_lines)))
    print(colored(get_message(lang, "select_package"), 'cyan'))

    while True:
        try:
            selection = int(input(f"Select a package number [1-{len(package_lines)}]: "))
            if 1 <= selection <= len(package_lines):
                selected_package = package_lines[selection - 1].split()[0]
                return selected_package
            else:
                print(colored(get_message(lang, "invalid_selection"), 'red'))
        except ValueError:
            print(colored(get_message(lang, "invalid_input"), 'red'))

def check_version():
    try:
        response = requests.get('https://raw.githubusercontent.com/KornineQ/KInstaller/master/ver.txt')
        latest_version = response.text.strip()
        current_version = '1.0.1"  

        if version_compare(current_version, latest_version) < 0:
            print(colored(get_message('en', 'outdated_version'), 'red'))
            sys.exit(1)
        elif version_compare(current_version, latest_version) > 0:
            print(colored(f"Warning: Your version {current_version} is newer than the latest version {latest_version}. This is unusual.", 'yellow'))
        else:
            print(colored(get_message('en', 'up_to_date'), 'green'))
    except requests.RequestException as e:
        print(colored(f"Failed to check for updates: {str(e)}", 'red'))

def kinstall(action, package, lang="pl"):
    if not check_arch_based():
        print(colored(get_message(lang, "not_arch"), 'red'))
        sys.exit(1)

    dist = distro.name()
    if dist == "Manjaro":
        print(colored(get_message(lang, "manjaro_warning"), 'yellow'))

    if action == '-S':
        print(colored(f"{get_message(lang, 'installing')} {package}...", 'blue'))
        stdout, stderr = run_command(f"sudo pacman -S {package} --noconfirm", timeout=120)
        if stderr:
            print(colored(stderr, 'red'))
            selected_package = search_and_select_package(package, lang)
            if selected_package:
                print(colored(f"Installing {selected_package}...", 'blue'))
                stdout, stderr = run_command(f"yay -S {selected_package} --noconfirm", timeout=120)
                if stderr:
                    print(colored(stderr, 'red'))
                    print(colored(get_message(lang, "package_not_found"), 'red'))
                else:
                    print(colored(stdout, 'green'))
        else:
            print(colored(stdout, 'green'))
    elif action == '-R':
        print(colored(f"{get_message(lang, 'removing')} {package}...", 'blue'))
        stdout, stderr = run_command(f"sudo pacman -R {package} --noconfirm", timeout=120)
        if stderr:
            print(colored(stderr, 'red'))
        else:
            print(colored(stdout, 'green'))
    else:
        print(colored(f"{get_message(lang, 'error')}: Unknown action '{action}'", 'red'))

if __name__ == "__main__":
    check_version()  

    if len(sys.argv) < 3:
        print(colored("Usage: kinstall <action> <package> [language]", 'red'))
        sys.exit(1)

    action = sys.argv[1]
    package = sys.argv[2]
    lang = sys.argv[3] if len(sys.argv) > 3 else "pl"

    try:
        kinstall(action, package, lang)
    except KeyboardInterrupt:
        print(colored("\nOperation cancelled by user.", 'yellow'))
        sys.exit(1)
    except Exception as e:
        print(colored(f"Unexpected error: {str(e)}", 'red'))
        sys.exit(1)
