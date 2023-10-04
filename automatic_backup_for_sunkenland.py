"""Automatic Backup for Sunkenland

If you execute this program, it will check for a "config.toml" file in the current directory. If there is no config file present,
it will create one. If needed, edit the config file and execute the program again.
If Sunkenland is closed after playing, it will create a backup of Sunkenland
"""
import os
import shutil
import datetime
from tkinter import messagebox
import subprocess
import time
import tomllib
import sys
import psutil

CONFIG_FILENAME = "config.toml"


def load_or_create_config_file():
    """Check if config file exists and load, otherwise create the file and exit"""
    if os.path.exists(CONFIG_FILENAME):
        with open(CONFIG_FILENAME, "rb") as already_existing_file:
            tom_file_config = tomllib.load(already_existing_file)

        return tom_file_config

    else:
        default_toml_file = r"""
# TOML File
#Set frequency (in seconds), how often the program will check if the game is running. Default: 3
check_if_game_is_still_running_frequency = 3

#possible options yes/no
#If 'yes', you will be asked before any action happens, if 'no' the program will do the actions without asking
ask_bevor_start = "yes"
ask_bevor_backup = "yes"

#Enter steam url of desktop shortcut
steam_game_url = "steam://rungameid/2080690"

#Enter the backup folder where to backup the characters and worlds to
backup_folder_characters = "%userprofile%\\appdata\\locallow\\Vector3 Studio\\Sunkenland\\Backup_Characters"

backup_folder_worlds = "%userprofile%\\appdata\\locallow\\Vector3 Studio\\Sunkenland\\Backup_Worlds"
"""

        with open(
            os.path.join(os.getcwd(), CONFIG_FILENAME), "w", encoding="utf8"
        ) as output_toml_file:
            output_toml_file.write(default_toml_file)
            messagebox.showinfo(
                "No config file found",
                f"A new config file was created at the following path. If needed please edit the config file and start the program again. {os.path.join(os.getcwd(), 'config.toml')} ",
            )
            sys.exit(
                "No config file found"
                f"A new config file was created at the following path. If needed please edit the config file and start the program again. {os.path.join(os.getcwd(), 'config.toml')} "
            )


def backup_game_save(backup_folder_characters, backup_folder_worlds):
    """This function will backup the save games to the specified backup folder

    Args:
        backup_folder_characters (string): The specified characters backup folder
        backup_folder_worlds (string): The specified worlds backup folder
    """

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    backup_folder_characters_with_timestamp = os.path.join(
        os.path.expandvars(rf"{backup_folder_characters}"), f"Backup_{timestamp}"
    )
    backup_folder_worlds_with_timestamp = os.path.join(
        os.path.expandvars(rf"{backup_folder_worlds}"), f"Backup_{timestamp}"
    )

    # Define the paths for the game save folder and backup folder
    save_folder_characters = os.path.expandvars(
        r"%userprofile%\\appdata\\locallow\\Vector3 Studio\\Sunkenland\\Characters"
    )
    save_folder_worlds = os.path.expandvars(
        r"%userprofile%\\appdata\\locallow\\Vector3 Studio\\Sunkenland\\Worlds"
    )

    # Copy the contents of the save folder to the backup folder
    try:
        shutil.copytree(save_folder_characters, backup_folder_characters_with_timestamp)
        shutil.copytree(save_folder_worlds, backup_folder_worlds_with_timestamp)

        messagebox.showinfo(
            "Backup Successful",
            f"Save games backed up to:\n{backup_folder_characters_with_timestamp} \n\nand:\n\n {backup_folder_worlds_with_timestamp} ",
        )
    except Exception as error:
        messagebox.showerror(
            "Backup Error",
            f"An error occurred while backing up save games:\n{str(error)}",
        )


def is_game_running():
    """Function to check if the game process is running"""
    for process in psutil.process_iter(attrs=["pid", "name"]):
        if "sunkenland.exe" in process.info["name"].lower():
            print("The game is currently running")
            return True
    print("The game is not running")
    return False


def open_game(steam_game_url):
    """This function starts the game and waits until it is running

    Args:
        steam_game_url (string): URL of the steam game
    """
    # Open the Steam game
    start_command = f"start {steam_game_url}"
    subprocess.Popen(start_command, shell=True)
    while is_game_running() is False:
        print("Checking if the game has been started. It is currently not running")
        time.sleep(1)
    print("The game has been started")


def check_game_status(check_if_game_is_still_running_frequency):
    """Check if the game is running and wait for it to close"""
    while is_game_running():
        print(
            f"The game is running, checking again in {check_if_game_is_still_running_frequency} seconds if the game was closed"
        )
        time.sleep(check_if_game_is_still_running_frequency)

    print("The game is closed now")


def ask_before_open_game(steam_game_url):
    """This function is using a 'messagebox.askokcancel' to ask if the game should be opened.
    If not, the program will exit

    Args:
        steam_game_url (string): URL of the steam game
    """
    if messagebox.askokcancel("Automatic Sunkenland Backup", "Open Sunkenland?"):
        open_game(steam_game_url)
    else:
        sys.exit("You choose exit")


def ask_before_backup_game(backup_folder_characters, backup_folder_worlds):
    """This function is using a 'messagebox.askokcancel' to ask if the game should be backed up.
    If not, the program will exit

    Args:
        backup_folder_characters (string): The specified characters backup folder
        backup_folder_worlds (string): The specified worlds backup folder
    """
    if messagebox.askokcancel("Automatic Sunkenland Backup", "Backup Sunkenland?"):
        backup_game_save(backup_folder_characters, backup_folder_worlds)
    else:
        sys.exit("You choose exit")


def main():
    """main function"""

    tomlconfig = load_or_create_config_file()

    if (tomlconfig["ask_bevor_start"]).lower() == "yes":
        ask_before_open_game(tomlconfig["steam_game_url"])
    else:
        open_game(tomlconfig["steam_game_url"])

    check_game_status(int((tomlconfig["check_if_game_is_still_running_frequency"])))

    if (tomlconfig["ask_bevor_backup"]).lower() == "yes":
        ask_before_backup_game(
            tomlconfig["backup_folder_characters"], tomlconfig["backup_folder_worlds"]
        )
    else:
        backup_game_save(
            tomlconfig["backup_folder_characters"],
            tomlconfig["backup_folder_worlds"],
        )


if __name__ == "__main__":
    main()
