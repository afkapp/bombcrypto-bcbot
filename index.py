from cv2 import cv2
from pyclick import HumanClicker
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import numpy as np
import mss
import pyautogui
import telegram
import os

if os.name == 'nt':
    import pygetwindow as bcbotma
    from pygetwindow import PyGetWindowException

from colorama import init, Fore, Style
init()

if os.name == 'posix':
    print(Fore.YELLOW +'The multi account is only supported on Windows OS.\nO multi account é compatível somente com Windows.', Style.RESET_ALL)
    input('Press Enter to continue without multi account...\n') 

if os.name != 'nt' and os.name != 'posix':
    print(Fore.RED +'Your operating system is unsupported.\nO seu sistema operacional não é compatível.', Style.RESET_ALL)
    os._exit(0)

import time
import sys
import yaml
import random
import requests

banner = ("""
	
******************************* BombCrypto Bot *********************************
────────────────────────────────────────────────────────────────────────────────
─██████████████───██████████████─██████████████───██████████████─██████████████─
─██░░░░░░░░░░██───██░░░░░░░░░░██─██░░░░░░░░░░██───██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██████░░██───██░░██████████─██░░██████░░██───██░░██████░░██─██████░░██████─
─██░░██──██░░██───██░░██─────────██░░██──██░░██───██░░██──██░░██─────██░░██─────
─██░░██████░░████─██░░██─────────██░░██████░░████─██░░██──██░░██─────██░░██─────
─██░░░░░░░░░░░░██─██░░██─────────██░░░░░░░░░░░░██─██░░██──██░░██─────██░░██─────
─██░░████████░░██─██░░██─────────██░░████████░░██─██░░██──██░░██─────██░░██─────
─██░░██────██░░██─██░░██─────────██░░██────██░░██─██░░██──██░░██─────██░░██─────
─██░░████████░░██─██░░██████████─██░░████████░░██─██░░██████░░██─────██░░██─────
─██░░░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░░░██─██░░░░░░░░░░██─────██░░██─────
─████████████████─██████████████─████████████████─██████████████─────██████─────
────────────────────────────────────────────────────────────────────────────────
                                                                                
********           https://github.com/afkapp/bombcrypto-bcbot           ********
********       Join Us on Telegram: https://t.me/bombcryptobcbot        ********
                                                                                
********************************************************************************
********************* Please consider buying me a coffee :) ********************
********************************************************************************
******** BUSD/BCOIN (BEP20): 0x8c38512beca8b0b06bf4e85f67ee64a7dcdaa11a ********
********************************************************************************

            ---> Press CTRL+C to kill the bot or send /stop on Telegram.

*******************************************************************************                           
	""")

print(Fore.GREEN + banner + Style.RESET_ALL)

Pause=[]

def readConfig():
    with open("./config/config.yaml", 'r', encoding='utf8') as s:
        stream = s.read()
    return yaml.safe_load(stream)

try:
    streamConfig = readConfig()
    afkapplang = streamConfig['lang']
    configThreshold = streamConfig['threshold']
    configTimeIntervals = streamConfig['time_intervals']
    metamaskData = streamConfig['metamask']
    chestData = streamConfig['value_chests']
    offsets = streamConfig['offsets']
except FileNotFoundError:
    print(Fore.RED +'Error: config.yaml file not found, rename EXAMPLE-config.yaml to config.yaml inside /config folder \nErro: Arquivo config.yaml não encontrado, renomear EXAMPLE-config.yaml para config.yaml dentro da pasta /config', Style.RESET_ALL)
    exit()

try:
    config_version_local = streamConfig['version']
except KeyError:
    print(Fore.RED +'Error: Please update the config.yaml file. \nErro: Por favor atualize o arquivo config.yaml', Style.RESET_ALL)
    exit()

config_version = '1.7.5' #Required config version

if config_version > config_version_local:
    print(Fore.RED +'Error: Please update the config.yaml file. \nErro: Por favor atualize o arquivo config.yaml', Style.RESET_ALL)
    exit()


PT = configTimeIntervals['Pause_Time']
PWAR = configTimeIntervals['Pause_With_All_Rest']

telegramIntegration = False
try:
    stream = open("./config/services/telegram.yaml", 'r', encoding='utf8')
    streamConfigTelegram = yaml.safe_load(stream)
    telegramIntegration = streamConfigTelegram['telegram_enable']
    telegramChatId = streamConfigTelegram['chat_ids']
    telegramBotToken = streamConfigTelegram['botfather_token']
    telegramCoinReport = streamConfigTelegram['enable_coin_report']
    telegramMapReport = streamConfigTelegram['enable_map_report']
    telegramFormatImage = streamConfigTelegram['format_of_image']
    heroesClickedTelegram = streamConfigTelegram['heroes_clicked_telegram']
    stream.close()
except FileNotFoundError:
    print('Info: Telegram not configure, rename EXAMPLE-telegram.yaml to telegram.yaml')
    heroesClickedTelegram = True
except KeyError:
    print(Fore.RED +'Error: Please update the telegram.yaml file. \nErro: Por favor atualize o arquivo telegram.yaml', Style.RESET_ALL)
    exit()

BtsHeraldIntegration = False
try:
    stream = open("./config/services/btsherald.yaml", 'r', encoding='utf8')
    streamBtsHerald = yaml.safe_load(stream)
    BtsHeraldIntegration= streamBtsHerald['herald_active']
    bhid = streamBtsHerald['key-herald']
    herald_label = streamBtsHerald['label']
    stream.close()
except FileNotFoundError:
    print('Info: BTS Herald not configure, rename EXAMPLE-btsherald.yaml to btsherald.yaml')

multi_account = False
try:
    stream = open("./config/services/multiaccount.yaml", 'r', encoding='utf8')
    streamMA = yaml.safe_load(stream)
    multi_account = streamMA['multi-account']
    stream.close()
except FileNotFoundError:
    print('Info: Multi Account not configure, rename EXAMPLE-multiaccount.yaml to multiaccount.yaml')

hc = HumanClicker()
pyautogui.PAUSE = streamConfig['time_intervals']['interval_between_movements']
pyautogui.FAILSAFE = False
general_check_time = 1
check_for_updates = 15

heroes_clicked = 0
heroes_clicked_total = 0
login_attempts = 0
next_refresh_heroes = configTimeIntervals['send_heroes_for_work'][0]
next_refresh_heroes_positions = configTimeIntervals['refresh_heroes_positions'][0]

go_work_img = cv2.imread('./images/targets/go-work.png')
home_img = cv2.imread('./images/targets/home.png')
arrow_img = cv2.imread('./images/targets/go-back-arrow.png')
full_screen_img = cv2.imread('./images/targets/full_screen.png')
hero_img = cv2.imread('./images/targets/hero-icon.png')
x_button_img = cv2.imread('./images/targets/x.png')
teasureHunt_icon_img = cv2.imread('./images/targets/treasure-hunt-icon.png')
ok_btn_img = cv2.imread('./images/targets/ok.png')
connect_wallet_btn_img = cv2.imread('./images/targets/connect-wallet.png')
sign_btn_img = cv2.imread('./images/targets/metamask_sign.png')
new_map_btn_img = cv2.imread('./images/targets/new_map_01.png')
green_bar = cv2.imread('./images/targets/green-bar.png')
full_stamina = cv2.imread('./images/targets/full-stamina.png')
character_indicator = cv2.imread('./images/targets/character_indicator_01.png')
error_img = cv2.imread('./images/targets/error_01.png')
metamask_unlock_img = cv2.imread('./images/targets/unlock_metamask.png')
metamask_cancel_button = cv2.imread(
    './images/targets/metamask_cancel_button.png')
puzzle_img = cv2.imread('./images/targets/puzzle.png')
piece = cv2.imread('./images/targets/piece.png')
robot = cv2.imread('./images/targets/robot.png')
slider = cv2.imread('./images/targets/slider.png')
chest_button = cv2.imread('./images/targets/treasure_chest.png')
coin_icon = cv2.imread('./images/targets/coin.png')
maintenance_popup = cv2.imread('./images/targets/maintenance.png')
chest1 = cv2.imread('./images/targets/chest1.png')
chest2 = cv2.imread('./images/targets/chest2.png')
chest3 = cv2.imread('./images/targets/chest3.png')
chest4 = cv2.imread('./images/targets/chest4.png')
key_adventure = cv2.imread('./images/targets/key.png')
prison = cv2.imread('./images/targets/prison.png')
rock = cv2.imread('./images/targets/rock_01.png')
allwork = cv2.imread('./images/targets/all_work.png')
allrest = cv2.imread('./images/targets/all_rest.png')
common = cv2.imread('./images/targets/common.png')
rest = cv2.imread('./images/targets/go_rest.png')

def readAfkAppLang():
    with open("./lang/"+afkapplang+".yaml", 'r', encoding='utf8') as l:
        stream = l.read()
    return yaml.safe_load(stream)

try:
    streamLang = readAfkAppLang()
    afkapp_bcbot_01 = streamLang['afkapp_bcbot_01']
    afkapp_bcbot_02 = streamLang['afkapp_bcbot_02']
    afkapp_bcbot_03 = streamLang['afkapp_bcbot_03']
    afkapp_bcbot_04 = streamLang['afkapp_bcbot_04']
    afkapp_bcbot_05 = streamLang['afkapp_bcbot_05']
    afkapp_bcbot_06 = streamLang['afkapp_bcbot_06']
    afkapp_bcbot_07 = streamLang['afkapp_bcbot_07']
    afkapp_bcbot_08 = streamLang['afkapp_bcbot_08']
    afkapp_bcbot_09 = streamLang['afkapp_bcbot_09']
    afkapp_bcbot_10 = streamLang['afkapp_bcbot_10']
    afkapp_bcbot_11 = streamLang['afkapp_bcbot_11']
    afkapp_bcbot_12 = streamLang['afkapp_bcbot_12']
    afkapp_bcbot_13 = streamLang['afkapp_bcbot_13']
    afkapp_bcbot_14 = streamLang['afkapp_bcbot_14']
    afkapp_bcbot_15 = streamLang['afkapp_bcbot_15']
    afkapp_bcbot_16 = streamLang['afkapp_bcbot_16']
    afkapp_bcbot_17 = streamLang['afkapp_bcbot_17']
    afkapp_bcbot_18 = streamLang['afkapp_bcbot_18']
    afkapp_bcbot_19 = streamLang['afkapp_bcbot_19']
    afkapp_bcbot_20 = streamLang['afkapp_bcbot_20']
    afkapp_bcbot_21 = streamLang['afkapp_bcbot_21']
    afkapp_bcbot_22 = streamLang['afkapp_bcbot_22']
    afkapp_bcbot_23 = streamLang['afkapp_bcbot_23']
    afkapp_bcbot_24 = streamLang['afkapp_bcbot_24']
    afkapp_bcbot_25 = streamLang['afkapp_bcbot_25']
    afkapp_bcbot_26 = streamLang['afkapp_bcbot_26']
    afkapp_bcbot_27 = streamLang['afkapp_bcbot_27']
    afkapp_bcbot_28 = streamLang['afkapp_bcbot_28']
    afkapp_bcbot_29 = streamLang['afkapp_bcbot_29']
    afkapp_bcbot_30 = streamLang['afkapp_bcbot_30']
    afkapp_bcbot_31 = streamLang['afkapp_bcbot_31']
    afkapp_bcbot_32 = streamLang['afkapp_bcbot_32']
    afkapp_bcbot_33 = streamLang['afkapp_bcbot_33']
    afkapp_bcbot_34 = streamLang['afkapp_bcbot_34']
    afkapp_bcbot_35 = streamLang['afkapp_bcbot_35']
    afkapp_bcbot_36 = streamLang['afkapp_bcbot_36']
    afkapp_bcbot_37 = streamLang['afkapp_bcbot_37']
    afkapp_bcbot_38 = streamLang['afkapp_bcbot_38']
    afkapp_bcbot_39 = streamLang['afkapp_bcbot_39']
    afkapp_bcbot_40 = streamLang['afkapp_bcbot_40']
    afkapp_bcbot_41 = streamLang['afkapp_bcbot_41']
    afkapp_bcbot_42 = streamLang['afkapp_bcbot_42']
    afkapp_bcbot_43 = streamLang['afkapp_bcbot_43']
    afkapp_bcbot_44 = streamLang['afkapp_bcbot_44']
    afkapp_bcbot_45 = streamLang['afkapp_bcbot_45']
    afkapp_bcbot_46 = streamLang['afkapp_bcbot_46']
    afkapp_bcbot_47 = streamLang['afkapp_bcbot_47']
    afkapp_bcbot_48 = streamLang['afkapp_bcbot_48']
    afkapp_bcbot_49 = streamLang['afkapp_bcbot_49']
    afkapp_bcbot_50 = streamLang['afkapp_bcbot_50']
    afkapp_bcbot_51 = streamLang['afkapp_bcbot_51']
    afkapp_bcbot_52 = streamLang['afkapp_bcbot_52']
    afkapp_bcbot_53 = streamLang['afkapp_bcbot_53']
    afkapp_bcbot_54 = streamLang['afkapp_bcbot_54']
    afkapp_bcbot_55 = streamLang['afkapp_bcbot_55']
    afkapp_bcbot_56 = streamLang['afkapp_bcbot_56']
    afkapp_bcbot_57 = streamLang['afkapp_bcbot_57']
    afkapp_bcbot_58 = streamLang['afkapp_bcbot_58']
    afkapp_bcbot_59 = streamLang['afkapp_bcbot_59']
    afkapp_bcbot_60 = streamLang['afkapp_bcbot_60']
    afkapp_bcbot_61 = streamLang['afkapp_bcbot_61']
    afkapp_bcbot_62 = streamLang['afkapp_bcbot_62']
    afkapp_bcbot_63 = streamLang['afkapp_bcbot_63']
    afkapp_bcbot_64 = streamLang['afkapp_bcbot_64']
    afkapp_bcbot_65 = streamLang['afkapp_bcbot_65']
    afkapp_bcbot_66 = streamLang['afkapp_bcbot_66']
    afkapp_bcbot_67 = streamLang['afkapp_bcbot_67']
    afkapp_bcbot_68 = streamLang['afkapp_bcbot_68']
    afkapp_bcbot_69 = streamLang['afkapp_bcbot_69']
    afkapp_bcbot_70 = streamLang['afkapp_bcbot_70']
    afkapp_bcbot_71 = streamLang['afkapp_bcbot_71']
    afkapp_bcbot_72 = streamLang['afkapp_bcbot_72']
    afkapp_bcbot_73 = streamLang['afkapp_bcbot_73']
    afkapp_bcbot_74 = streamLang['afkapp_bcbot_74']
    afkapp_bcbot_75 = streamLang['afkapp_bcbot_75']

    
except FileNotFoundError:
    print('Error: The language file was not found.')
    print('Erro: O arquivo do idioma não foi encontrado.')
    exit()

def dateFormatted(format = '%Y-%m-%d %H:%M:%S'):
  datetime = time.localtime()
  formatted = time.strftime(format, datetime)
  return formatted

def logger(message, telegram=False, emoji=None):
    formatted_datetime = dateFormatted()
    console_message = "{} - {}".format(formatted_datetime, message)
    service_message = "⏰{}\n{} {}".format(formatted_datetime, emoji, message)
    if emoji is not None and streamConfig['emoji'] is True:
        console_message = "{} - {} {}".format(
            formatted_datetime, emoji, message)

    print(console_message)

    if telegram == True:
        sendTelegramMessage(service_message)

    if (streamConfig['save_log_to_file'] == True):
        logger_file = open("./logs/logger.log", "a", encoding='utf-8')
        logger_file.write(console_message + '\n')
        logger_file.close()
    return True

def PauseStatus():
    return Pause

def checkFileExist(filePath):
    try:
        with open(filePath, 'r') as f:
            return True
    except FileNotFoundError as e:
        return False
    except IOError as e:
        return False

# Initialize telegram
updater = None
if telegramIntegration == True:
    logger(afkapp_bcbot_06, emoji='📱')
    updater = Updater(telegramBotToken)

    try:
        TBot = telegram.Bot(token=telegramBotToken)

        def send_print(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 '+afkapp_bcbot_07)
            screenshot = printScreen()
            cv2.imwrite('./logs/print-report.%s' %
                        telegramFormatImage, screenshot)
            update.message.reply_photo(photo=open(
                './logs/print-report.%s' % telegramFormatImage, 'rb'))

        def send_id(update: Update, context: CallbackContext) -> None:
            update.message.reply_text(
                f'🆔 '+afkapp_bcbot_08+' https://t.me/btsherald_bot')

        def send_map(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 '+afkapp_bcbot_07)
            if sendMapReport() is None:
                update.message.reply_text('😿 '+afkapp_bcbot_09)

        def send_bcoin(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 '+afkapp_bcbot_07)
            if sendBCoinReport() is None:
                update.message.reply_text('😿 '+afkapp_bcbot_09)

        def send_wallet(update: Update, context: CallbackContext) -> None:
            update.message.reply_text(
                f'🎁 BUSD/BCOIN(BEP20): \n\n 0x8c38512beca8b0b06bf4e85f67ee64a7dcdaa11a \n\n '+afkapp_bcbot_10+' 😀')

        def send_telegram_invite(update: Update, context: CallbackContext) -> None:
            update.message.reply_text(
                f'💖 '+afkapp_bcbot_11+' https://t.me/bombcryptobcbot')

        def send_herald(update: Update, context: CallbackContext) -> None:
            update.message.reply_text(
                f''+afkapp_bcbot_12)

        def send_vps(update: Update, context: CallbackContext) -> None:
            update.message.reply_text(
                f''+afkapp_bcbot_13)

        def send_refresh(update: Update, context: CallbackContext) -> None:
            pyautogui.hotkey('ctrl', 'shift', 'r')
            waitForImage(connect_wallet_btn_img)
            login()

        def send_allwork(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 '+afkapp_bcbot_07)
            if sendallworkReport() == None:
                update.message.reply_text('✔️ '+afkapp_bcbot_64)
        
        def send_allrest(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 '+afkapp_bcbot_07)
            if sendallrestReport() == None:
                update.message.reply_text('✔️ '+afkapp_bcbot_64)
        
        def send_pause(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 '+afkapp_bcbot_07)
            if len(Pause) == 1:
                update.message.reply_text('⚠️ '+afkapp_bcbot_69)
            if len(Pause) == 0:
                Pause.append(1)
                update.message.reply_text('✔️ '+afkapp_bcbot_68)

        def send_continue(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 '+afkapp_bcbot_07)
            if len(Pause) == 0:
                update.message.reply_text('⚠️ '+afkapp_bcbot_70)
            if len(Pause) == 1:
                #time.sleep(0.25)
                #Pause.remove(1)
                #
                update.message.reply_text('💡 '+afkapp_bcbot_65)
                #update.message.reply_text('✔️ '+afkapp_bcbot_67)

        def send_closevps(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 '+afkapp_bcbot_07)
            if os.name != 'nt':
                update.message.reply_text('⚠️ '+afkapp_bcbot_72)
            if os.name == 'nt':
                FE = checkFileExist('BtsCloseVPS.exe')
                if FE != True:
                    update.message.reply_text('🖥️ '+afkapp_bcbot_73)
                if FE == True:
                    update.message.reply_text('✔️ '+afkapp_bcbot_71)
                    os.startfile("BtsCloseVPS.exe")

        def send_stop(update: Update, context: CallbackContext) -> None:
            logger(afkapp_bcbot_14, telegram=True, emoji='🛑')
            os._exit(0)
               
        commands = [
            ['print', send_print],
            ['id', send_id],
            ['map', send_map],
            ['bcoin', send_bcoin],
            ['refresh', send_refresh],
            ['donation', send_wallet],
            ['invite', send_telegram_invite],
            ['herald', send_herald],
            ['vps', send_vps],
            ['allwork', send_allwork],
            ['allrest', send_allrest],
            ['pause', send_pause],
            ['continue', send_continue],
            ['closevps', send_closevps],
            ['stop', send_stop]
        ]

        for command in commands:
            updater.dispatcher.add_handler(
                CommandHandler(command[0], command[1]))

        updater.start_polling()
        # updater.idle()
    except:
        logger(afkapp_bcbot_15, emoji='🤖')


def sendTelegramMessage(message):
    if telegramIntegration == False:
        return
    try:
        if(len(telegramChatId) > 0):
            for chat_id in telegramChatId:
                TBot.send_message(text=message, chat_id=chat_id)
    except:
        #logger(afkapp_bcbot_16, emoji='📄')
        return

def sendTelegramPrint():
    if telegramIntegration == False:
        return
    try:
        if(len(telegramChatId) > 0):
            screenshot = printScreen()
            cv2.imwrite('./logs/print-report.%s' %
                        telegramFormatImage, screenshot)
            for chat_id in telegramChatId:
                TBot.send_photo(chat_id=chat_id, photo=open(
                    './logs/print-report.%s' % telegramFormatImage, 'rb'))
    except:
        logger(afkapp_bcbot_16, emoji='📄')


def sendPossibleAmountReport(baseImage):
    if telegramIntegration == False:
        return
    c1 = len(positions(chest1, configThreshold['chest'], baseImage, True))
    c2 = len(positions(chest2, configThreshold['chest'], baseImage, True))
    c3 = len(positions(chest3, configThreshold['chest'], baseImage, True))
    c4 = len(positions(chest4, configThreshold['chest'], baseImage, True))
    ckey = len(positions(key_adventure, configThreshold['chest'], baseImage, True))
    cprison = len(positions(prison, configThreshold['chest'], baseImage, True))
    crock = len(positions(rock, configThreshold['chest'], baseImage, True))

    value1 = c1 * chestData["value_chest1"]
    value2 = c2 * chestData["value_chest2"]
    value3 = c3 * chestData["value_chest3"]
    value4 = c4 * chestData["value_chest4"]

    total = value1 + value2 + value3 + value4
    total_items = c1 + c2 + c3 + c4 + crock + ckey + cprison

    report = """
"""+afkapp_bcbot_17+"""

🟤 - """+str(c1)+"""
🟣 - """+str(c2)+"""
🟡 - """+str(c3)+"""
🔵 - """+str(c4)+"""
🪨 - """+str(crock)+"""
🔑 - """+str(ckey)+"""
🎁 - """+str(cprison)+"""

🗺️ - """'Total: '+str(total_items)+"""

🤑 """+afkapp_bcbot_18+""" """+f'{total:.3f} BCoin'+"""
"""
    logger(report, telegram=True)
    if cprison > 0:
        logger(afkapp_bcbot_74, telegram=True, emoji='🎁')
        #Notify by BTS Herald (Coming Soon)
    
    if ckey > 0:
        logger(afkapp_bcbot_75, telegram=True, emoji='🔑')

def sendBCoinReport():
    if telegramIntegration == False:
        return
    if(len(telegramChatId) <= 0 or telegramCoinReport is False):
        return

    if currentScreen() == "main":
        if clickButton(teasureHunt_icon_img):
            time.sleep(2)
    elif currentScreen() == "character":
        if clickButton(x_button_img):
            time.sleep(2)
            if clickButton(teasureHunt_icon_img):
                time.sleep(2)
    elif currentScreen() == "thunt":
        time.sleep(2)
    else:
        return

    clickButton(chest_button)

    sleep(5, 15)

    coin = positions(coin_icon, return_0=True)
    if len(coin) > 0:
        x, y, w, h = coin[0]

        with mss.mss() as sct:
            sct_img = np.array(
                sct.grab(sct.monitors[streamConfig['monitor_to_use']]))
            crop_img = sct_img[y:y+h, x:x+w]
            cv2.imwrite('./logs/bcoin-report.%s' %
                        telegramFormatImage, crop_img)
            time.sleep(1)
            try:
                for chat_id in telegramChatId:
                    # TBot.send_document(chat_id=chat_id, document=open('bcoin-report.png', 'rb'))
                    TBot.send_photo(chat_id=chat_id, photo=open(
                        './logs/bcoin-report.%s' % telegramFormatImage, 'rb'))
            except:
                logger(afkapp_bcbot_19, emoji='😿')
    clickButton(x_button_img)
    logger(afkapp_bcbot_20, telegram=True, emoji='📄')
    return True


def sendMapReport():
    if telegramIntegration == False:
        return
    if(len(telegramChatId) <= 0 or telegramMapReport is False):
        return

    if currentScreen() == "main":
        if clickButton(teasureHunt_icon_img):
            time.sleep(2)
    elif currentScreen() == "character":
        if clickButton(x_button_img):
            time.sleep(2)
            if clickButton(teasureHunt_icon_img):
                time.sleep(2)
    elif currentScreen() == "thunt":
        time.sleep(2)
    else:
        return

    back = positions(arrow_img, return_0=True)
    full_screen = positions(full_screen_img, return_0=True)
    if len(back) <= 0 or len(full_screen) <= 0:
        return
    x, y, _, _ = back[0]
    x1, y1, w, h = full_screen[0]
    newY0 = y
    newY1 = y1
    newX0 = x
    newX1 = x1 + w

    with mss.mss() as sct:
        sct_img = np.array(
            sct.grab(sct.monitors[streamConfig['monitor_to_use']]))
        crop_img = sct_img[newY0:newY1, newX0:newX1]
        # resized = cv2.resize(crop_img, (500, 250))

        cv2.imwrite('./logs/map-report.%s' % telegramFormatImage, crop_img)
        time.sleep(1)
        try:
            for chat_id in telegramChatId:
                # TBot.send_document(chat_id=chat_id, document=open('map-report.png', 'rb'))
                TBot.send_photo(chat_id=chat_id, photo=open(
                    './logs/map-report.%s' % telegramFormatImage, 'rb'))
        except:
            logger(afkapp_bcbot_19, emoji='😿')

        try:
            sendPossibleAmountReport(sct_img[:, :, :3])
        except:
            logger(afkapp_bcbot_21, telegram=True, emoji='😿')

    clickButton(x_button_img)
    logger(afkapp_bcbot_22, telegram=True, emoji='📄')
    return True

def sendallworkReport():
    if telegramIntegration == False:
        return
    if(len(telegramChatId) <= 0):
        return
    if currentScreen() == "main":
            time.sleep(2)
    elif currentScreen() == "character":
        if clickButton(x_button_img):
            time.sleep(2)
    elif currentScreen() == "thunt":
        if clickButton(arrow_img):
            time.sleep(2)
    else:
        return
    
    clickButton(hero_img)    
    waitForImage(home_img)
    clickButton(allwork)
    clickButton(x_button_img)
    clickButton(teasureHunt_icon_img)
    sleep(5, 15)
    clickButton(x_button_img)
    logger('All working report sent', telegram=True, emoji='📄')

def sendallrestReport():
    if telegramIntegration == False:
        return
    if(len(telegramChatId) <= 0):
        return
    if currentScreen() == "main":
            time.sleep(2)
    elif currentScreen() == "character":
        if clickButton(x_button_img):
            time.sleep(2)
    elif currentScreen() == "thunt":
        if clickButton(arrow_img):
            time.sleep(2)
    else:
        return
    
    clickButton(hero_img)    
    waitForImage(home_img)
    clickButton(allrest)
    clickButton(x_button_img)
    clickButton(teasureHunt_icon_img)
    sleep(5, 15)    
    clickButton(x_button_img)
    logger('All resting report sent', telegram=True, emoji='📄')

#INTEGRATION WITH BTS HERALD - GET A NOTIFICATION IF THE BOT STOPS | https://herald.btscenter.net
def herald():
    if BtsHeraldIntegration == True and bhid != '':
        herald = requests.get('https://herald.btscenter.net/monitor/?app=BCBOT&lang='+afkapplang+'&label='+herald_label+'&bhid='+bhid)
        #  --> You can DELETE the above line if you are not going to use the BTS Herald service: https://herald.btscenter.net

        #  --> If you use the BTS Herald service, we'll collect the following data:
        #
        #  * afkapplang = Language used in your bot
        #  * herald_label = The tag/name you chose for the bot on this machine
        #  * bhid = Your BTS Herald Key
        #
        #  --> SCAM? Definitely not is a SCAM.
        #  --> Are you claiming it is a SCAM?
        #
        # You're using open source scripts, copying the work of other, not contributing anything, talking nonsense and no proof.
        # Envy kills, if you were creating something useful, wouldn't have time for this.
        
def clickButton(img, name=None, timeout=3, threshold=configThreshold['default']):
    if not name is None:
        pass
    start = time.time()
    clicked = False
    while(not clicked):
        matches = positions(img, threshold=threshold)
        if(matches is False):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            continue

        x, y, w, h = matches[0]
        # pyautogui.moveTo(x+(w/2),y+(h/2),1)
        # pyautogui.moveTo(int(random.uniform(x, x+w)),int(random.uniform(y, y+h)),1)
        hc.move((int(random.uniform(x, x+w)), int(random.uniform(y, y+h))), 1)
        pyautogui.click()
        return True


def printScreen():
    with mss.mss() as sct:
        # The screen part to capture
        # Grab the data
        sct_img = np.array(
            sct.grab(sct.monitors[streamConfig['monitor_to_use']]))
        return sct_img[:, :, :3]


def positions(target, threshold=configThreshold['default'], base_img=None, return_0=False):
    if base_img is None:
        img = printScreen()
    else:
        img = base_img

    w = target.shape[1]
    h = target.shape[0]

    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    if return_0 is False:
        if len(rectangles) > 0:
            # sys.stdout.write("\nGet_coords. " + str(rectangles) + " " + str(weights) + " " + str(w) + " " + str(h) + " ")
            return rectangles
        else:
            return False
    else:
        return rectangles

def show(rectangles=None, img=None):

    if img is None:
        with mss.mss() as sct:
            img = np.array(
                sct.grab(sct.monitors[streamConfig['monitor_to_use']]))

    if rectangles is not None:
        for (x, y, w, h) in rectangles:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)


def scroll():
    offset = offsets['character_indicator']
    offset_random = random.uniform(offset[0], offset[1])

    # width, height = pyautogui.size()
    # pyautogui.moveTo(width/2-200, height/2,1)
    character_indicator_pos = positions(character_indicator)
    if character_indicator_pos is False:
        return

    x, y, w, h = character_indicator_pos[0]
    hc.move((int(x+(w/2)), int(y+h+offset_random)), np.random.randint(1, 2))

    if not streamConfig['use_click_and_drag_instead_of_scroll']:
        pyautogui.click()
        pyautogui.scroll(-streamConfig['scroll_size'])
    else:
        # pyautogui.dragRel(0,-streamConfig['click_and_drag_amount'],duration=1, button='left')
        pyautogui.mouseDown(button='left')
        hc.move((int(x), int(
            y+(-streamConfig['click_and_drag_amount']))), np.random.randint(1, 2))
        pyautogui.mouseUp(button='left')


def clickButtons():
    buttons = positions(
        go_work_img, threshold=configThreshold['go_to_work_btn'])
    offset = offsets['work_button_all']

    if buttons is False:
        return

    if streamConfig['debug'] is not False:
        logger('%d buttons detected' % len(buttons), emoji='✔️')

    for (x, y, w, h) in buttons:
        offset_random = random.uniform(offset[0], offset[1])
        # pyautogui.moveTo(x+(w/2),y+(h/2),1)
        hc.move((int(x+offset_random), int(y+(h/2))), np.random.randint(1, 2))
        pyautogui.click()
        global heroes_clicked_total
        global heroes_clicked
        heroes_clicked_total = heroes_clicked_total + 1
        # cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if heroes_clicked > 15:
            logger(afkapp_bcbot_23,
                   telegram=True, emoji='⚠️')
            return
        sleep(1, 3)
    logger('Clicking in %d heroes detected.' %
           len(buttons), telegram=False, emoji='👆')
    return len(buttons)


def isWorking(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True


def clickGreenBarButtons():
    offset = offsets['work_button']
    green_bars = positions(green_bar, threshold=configThreshold['green_bar'])
    buttons = positions(
        go_work_img, threshold=configThreshold['go_to_work_btn'])

    if green_bars is False or buttons is False:
        return

    if streamConfig['debug'] is not False:
        logger('%d green bars detected' % len(green_bars), emoji='🟩')
        logger('%d buttons detected' % len(buttons), emoji='🔳')

    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('Clicking in %d heroes with green bar detected.' %
               len(not_working_green_bars), telegram=False, emoji='👆')

    # se tiver botao com y maior que bar y-10 e menor que y+10
    for (x, y, w, h) in not_working_green_bars:
        offset_random = random.uniform(offset[0], offset[1])
        # isWorking(y, buttons)
        # pyautogui.moveTo(x+offset+(w/2),y+(h/2),1)
        hc.move((int(x+offset_random+(w/2)), int(y+(h/2))),
                np.random.randint(1, 2))
        pyautogui.click()
        global heroes_clicked_total
        global heroes_clicked
        heroes_clicked_total = heroes_clicked_total + 1
        if heroes_clicked > 15:
            logger(afkapp_bcbot_23,
                   telegram=True, emoji='⚠️')
            return
        # cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        sleep(1, 3)
    return len(not_working_green_bars)


def clickFullBarButtons():
    offset = offsets['work_button_full']
    full_bars = positions(full_stamina, threshold=configThreshold['full_bar'])
    buttons = positions(
        go_work_img, threshold=configThreshold['go_to_work_btn'])

    if full_bars is False or buttons is False:
        return

    if streamConfig['debug'] is not False:
        logger('%d FULL bars detected' % len(full_bars), emoji='🟩')
        logger('%d buttons detected' % len(buttons), emoji='🔳')

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('Clicking in %d heroes with FULL bar detected.' %
               len(not_working_full_bars), telegram=True, emoji='👆')

    for (x, y, w, h) in not_working_full_bars:
        offset_random = random.uniform(offset[0], offset[1])
        # pyautogui.moveTo(x+offset+(w/2),y+(h/2),1)
        hc.move((int(x+offset_random+(w/2)), int(y+(h/2))),
                np.random.randint(1, 2))
        pyautogui.click()
        global heroes_clicked_total
        global heroes_clicked
        heroes_clicked_total = heroes_clicked_total + 1
        if heroes_clicked > 15:
            logger(afkapp_bcbot_23,
                   telegram=True, emoji='⚠️')
            return
        sleep(1, 3)
    return len(not_working_full_bars)


def currentScreen():
    if positions(arrow_img) is not False:
        # sys.stdout.write("\nThunt. ")
        return "thunt"
    elif positions(teasureHunt_icon_img) is not False:
        # sys.stdout.write("\nmain. ")
        return "main"
    elif positions(connect_wallet_btn_img) is not False:
        # sys.stdout.write("\nlogin. ")
        return "login"
    elif positions(character_indicator) is not False:
        # sys.stdout.write("\ncharacter. ")
        return "character"
    else:
        # sys.stdout.write("\nUnknown. ")
        return "unknown"


def goToHeroes():
    if currentScreen() == "thunt":
        if clickButton(arrow_img):
            sleep(1, 3)
            if clickButton(hero_img):
                sleep(1, 3)
                waitForImage(home_img)
    if currentScreen() == "main":
        if clickButton(hero_img):
            sleep(1, 3)
            waitForImage(home_img)
    if currentScreen() == "unknown" or currentScreen() == "login":
        checkLogout()

def goToTreasureHunt():
    if currentScreen() == "main":
        clickButton(teasureHunt_icon_img)
    if currentScreen() == "character":
        herald()
        if clickButton(x_button_img):
            sleep(1, 3)
            clickButton(teasureHunt_icon_img)
            #herald()
    if currentScreen() == "unknown" or currentScreen() == "login":
        checkLogout()


def refreshHeroesPositions():
    logger(afkapp_bcbot_31, emoji='🔃')
    global next_refresh_heroes_positions
    next_refresh_heroes_positions = random.uniform(
        configTimeIntervals['refresh_heroes_positions'][0], configTimeIntervals['refresh_heroes_positions'][1])
    if currentScreen() == "thunt":
        if clickButton(arrow_img):
            time.sleep(5)
    if currentScreen() == "main":
        if clickButton(teasureHunt_icon_img):
            return True
        else:
            return False
    else:
        return False


def login():
    global login_attempts

    randomMouseMovement()

    if clickButton(connect_wallet_btn_img):
        logger(afkapp_bcbot_32, emoji='🎉')
        time.sleep(2)
        waitForImage((sign_btn_img, metamask_unlock_img), multiple=True)

    metamask_unlock_coord = positions(metamask_unlock_img)
    if metamask_unlock_coord is not False:
        if(metamaskData["enable_login_metamask"] is False):
            logger(
                'Metamask locked! But login with password is disabled, exiting', emoji='🔒')
            exit()
        logger('Found unlock button. Waiting for password', emoji='🔓')
        password = metamaskData["password"]
        pyautogui.typewrite(password, interval=0.1)
        sleep(1, 3)
        if clickButton(metamask_unlock_img):
            logger('Unlock button clicked', emoji='🔓')

    if clickButton(sign_btn_img):
        logger('Found sign button. Waiting to check if logged in', emoji='✔️')
        time.sleep(5)
        if clickButton(sign_btn_img):  # twice because metamask glitch
            logger(
                'Found glitched sign button. Waiting to check if logged in', emoji='✔️')
        # time.sleep(25)
        waitForImage(teasureHunt_icon_img, timeout=30)
        handleError()

    if currentScreen() == "main":
        logger(afkapp_bcbot_38, telegram=True, emoji='🎉')
        time.sleep(5)
        return True
    else:
        logger(afkapp_bcbot_39, emoji='😿')
        login_attempts += 1

        if (login_attempts > 3):
            sendTelegramPrint()
            logger(afkapp_bcbot_40, telegram=True, emoji='🔃')
            # pyautogui.hotkey('ctrl', 'f5')
            pyautogui.hotkey('ctrl', 'shift', 'r')
            login_attempts = 0

            if clickButton(metamask_cancel_button):
                logger(afkapp_bcbot_41, emoji='🙀')

            waitForImage(connect_wallet_btn_img)

        login()

    handleError()


def handleError():
    if positions(error_img, configThreshold['error']) is not False:
        sendTelegramPrint()
        logger(afkapp_bcbot_42, telegram=True, emoji='💥')
        clickButton(ok_btn_img)
        logger(afkapp_bcbot_43, telegram=True, emoji='🔃')
        # pyautogui.hotkey('ctrl', 'f5')
        pyautogui.hotkey('ctrl', 'shift', 'r')
        waitForImage(connect_wallet_btn_img)
        login()
    else:
        return False


def getMoreHeroes():
    global next_refresh_heroes
    global heroes_clicked

    logger(afkapp_bcbot_44, emoji='🏢')

    goToHeroes()

    if streamConfig['select_heroes_mode'] == "full":
        logger(afkapp_bcbot_45, emoji='⚒️')
    elif streamConfig['select_heroes_mode'] == "green":
        logger(afkapp_bcbot_46, emoji='⚒️')
    else:
        logger(afkapp_bcbot_47, emoji='⚒️')

    buttonsClicked = 0
    heroes_clicked = 0
    empty_scrolls_attempts = streamConfig['scroll_attempts']
    next_refresh_heroes = random.uniform(
        configTimeIntervals['send_heroes_for_work'][0], configTimeIntervals['send_heroes_for_work'][1])

    while(empty_scrolls_attempts > 0):
        if streamConfig['select_heroes_mode'] == 'full':
            buttonsClicked = clickFullBarButtons()
            if buttonsClicked is not None:
                heroes_clicked += buttonsClicked
        elif streamConfig['select_heroes_mode'] == 'green':
            buttonsClicked = clickGreenBarButtons()
            if buttonsClicked is not None:
                heroes_clicked += buttonsClicked
        else:
            buttonsClicked = clickButtons()
            if buttonsClicked is not None:
                heroes_clicked += buttonsClicked

        if buttonsClicked == 0 or buttonsClicked is None:
            empty_scrolls_attempts = empty_scrolls_attempts - 1
            scroll()
        sleep(1, 3)
    logger('{} '.format(
        heroes_clicked_total)+afkapp_bcbot_48, telegram=heroesClickedTelegram, emoji='🦸')
    goToTreasureHunt()

def checkLogout():
    if currentScreen() == "unknown" or currentScreen() == "login":
        if positions(connect_wallet_btn_img) is not False:
            sendTelegramPrint()
            logger(afkapp_bcbot_49, telegram=True, emoji='😿')
            logger(afkapp_bcbot_43, telegram=True, emoji='🔃')
            pyautogui.hotkey('ctrl', 'shift', 'r')
            waitForImage(connect_wallet_btn_img)
            login()
        elif positions(sign_btn_img):
            logger(afkapp_bcbot_50, telegram=True, emoji='✔️')
            if clickButton(metamask_cancel_button):
                logger(afkapp_bcbot_41,
                       telegram=True, emoji='🙀')
        else:
            return False

    else:
        return False


def waitForImage(imgs, timeout=30, threshold=0.5, multiple=False):
    start = time.time()
    while True:
        if multiple is not False:
            for img in imgs:
                matches = positions(img, threshold=threshold)
                if matches is False:
                    hast_timed_out = time.time()-start > timeout
                    if hast_timed_out is not False:
                        return False
                    continue
                return True
        else:
            matches = positions(imgs, threshold=threshold)
            if matches is False:
                hast_timed_out = time.time()-start > timeout
                if hast_timed_out is not False:
                    return False
                continue
            return True


def clickNewMap():
    logger(afkapp_bcbot_51, emoji='🗺️')
    sleep(1, 2)
    sleep(2, 3)
    sendMapReport()
    sleep(3, 5)
    sendBCoinReport()


def sleep(min, max):
    sleep = random.uniform(min, max)
    randomMouseMovement()
    return time.sleep(sleep)


def randomMouseMovement():
    x, y = pyautogui.size()
    x = np.random.randint(0, x)
    y = np.random.randint(0, y)
    hc.move((int(x), int(y)), np.random.randint(1, 3))


def checkUpdates():
    data = requests.get(
        'https://raw.githubusercontent.com/afkapp/bombcrypto-bcbot/main/config/version.yaml')
    try:
        streamVersionGithub = yaml.safe_load(data.text)
        version = streamVersionGithub['version']
        emergency = streamVersionGithub['emergency']
    except KeyError:
        logger('Version not found in github, securety problem', emoji='💥')
        version = "0"

    print(afkapp_bcbot_53+' ' + version)

    try:
        streamVersionLocal = open("./config/version.yaml", 'r', encoding='utf8')
        streamVersion = yaml.safe_load(streamVersionLocal)
        versionLocal = streamVersion['version']
        streamVersionLocal.close()
    except FileNotFoundError:
        versionLocal = None

    if (emergency == 'true' and version > versionLocal):
        os._exit(0)

    if versionLocal is not None:
        print(afkapp_bcbot_54+' ' + versionLocal)
        if version > versionLocal:
            logger(afkapp_bcbot_55+' ' + version +
                   ' '+afkapp_bcbot_56, telegram=True, emoji='🎉'),
    else:
        logger(afkapp_bcbot_57,
               telegram=True, emoji='💥')
        exit()

def checkThreshold():
    global configThreshold
    newStream = readConfig()
    newConfigThreshold = newStream['threshold']

    if newConfigThreshold != configThreshold:
        configThreshold = newConfigThreshold
        logger(afkapp_bcbot_58, telegram=False, emoji='⚙️')

def bcbotsingle():
    print(Fore.YELLOW +afkapp_bcbot_59, Style.RESET_ALL)
    last = {
        "login": 0,
        "heroes": 0,
        "new_map": 0,
        "refresh_heroes": 0,
        "check_updates": 0
    }

    while True:
        if currentScreen() == "login":
            login()

        handleError()

        now = time.time()

        ps=PauseStatus()
        if len(ps) == 1:
            logger(afkapp_bcbot_66, telegram=True, emoji='🤖')
            time.sleep(PT*60)
            if len(ps) == 0:
                logger('Debug of continue', telegram=True, emoji='🤖') #Test
            if len(ps) == 1:
                Pause.remove(1)
                logger(afkapp_bcbot_67, telegram=True, emoji='🤖')

        if now - last["heroes"] > next_refresh_heroes * 60:
            last["heroes"] = now
            last["refresh_heroes"] = now
            getMoreHeroes()

        if currentScreen() == "main":
            if clickButton(teasureHunt_icon_img):
                logger('Entering treasure hunt', emoji='▶️')
                last["refresh_heroes"] = now

        if currentScreen() == "thunt":
            if clickButton(new_map_btn_img):
                last["new_map"] = now
                clickNewMap()

        if currentScreen() == "character":
            clickButton(x_button_img)
            sleep(1, 3)

        if now - last["refresh_heroes"] > next_refresh_heroes_positions * 60:
            last["refresh_heroes"] = now
            refreshHeroesPositions()

        if now - last["check_updates"] > check_for_updates * 60:
            last["check_updates"] = now
            checkUpdates()

        checkLogout()
        sys.stdout.flush()
        time.sleep(1)
        checkThreshold()

def bcbotmaw():
    print(Fore.GREEN +afkapp_bcbot_61, Style.RESET_ALL)

    windows = []
    
    for w in bcbotma.getWindowsWithTitle('bombcrypto'):
        windows.append({
            "window": w,
            "login" : 0,
            "heroes" : 0,
            "new_map" : 0,
            "refresh_heroes" : 0
            })

    while True:
        if currentScreen() == "login":
            login()

        handleError()

        now = time.time()
        
        ps=PauseStatus()
        if len(ps) == 1:
            logger(afkapp_bcbot_66, telegram=True, emoji='🤖')
            time.sleep(PT*60)
            if len(ps) == 0:
                logger('Debug of continue', telegram=True, emoji='🤖') #Test
            if len(ps) == 1:
                Pause.remove(1)
                logger(afkapp_bcbot_67, telegram=True, emoji='🤖')

        for last in windows:
            try:
                last["window"].maximize()
                last["window"].activate()
            except:
                last["window"].minimize()
                last["window"].maximize()
                last["window"].activate()
            time.sleep(2)
        
            if now - last["heroes"] > next_refresh_heroes * 60:
                last["heroes"] = now
                last["refresh_heroes"] = now
                getMoreHeroes()

            if currentScreen() == "main":
                if clickButton(teasureHunt_icon_img):
                    logger('Entering treasure hunt', emoji='▶️')
                    last["refresh_heroes"] = now

            if currentScreen() == "thunt":
                if clickButton(new_map_btn_img):
                    last["new_map"] = now
                    clickNewMap()

            if currentScreen() == "character":
                clickButton(x_button_img)
                sleep(1, 3)

            if now - last["refresh_heroes"] > next_refresh_heroes_positions * 60:
                last["refresh_heroes"] = now
                refreshHeroesPositions()

            checkLogout()
            sys.stdout.flush()
            time.sleep(general_check_time)
            checkThreshold()

def main():

    checkUpdates()
    #input('Press Enter to start the bot...\n')
    logger('Starting bot...', telegram=True, emoji='🤖')
    logger(afkapp_bcbot_11+' https://t.me/bombcryptobcbot', telegram=True, emoji='💖')
    logger(afkapp_bcbot_63, telegram=True, emoji='ℹ️')

    if multi_account != True and os.name == 'nt':
        bcbotsingle() 
    
    if multi_account == True and os.name == 'nt':
        bcbotmaw() 

    if os.name == 'posix':
        bcbotsingle()  

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger(afkapp_bcbot_14, telegram=True, emoji='😓')
        if(updater):
            updater.stop()
        exit()
