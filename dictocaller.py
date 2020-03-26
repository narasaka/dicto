#!/usr/bin/env python3

import requests
import bs4
import pgi
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key, Controller
pgi.require_version('Notify', '0.7')
from pgi.repository import Notify


def show_notif(word, alert):
    #display notif
    Notify.init('Dictionary')
    notif = Notify.Notification.new(word, alert, 'dialog-information')
    notif.set_urgency(2)
    notif.show()

    #clean up
    Notify.uninit()


def decision():

    if 'https://www.dictionary.com/misspelling' in page.url: #if word is not found in dictionary
        alert = 'Word/phrase not found. Is that english?'
        print(clipboard + ' not found.')
        show_notif(clipboard, alert) #display notification

    else: #if word is found
        word = soup.find('h1').text #name of word
        pron = soup.find('span', {'class':'pron-spell-content css-z3mf2 evh0tcl2'}).text #pronunciation

        sec_children = soup.find('div', {'class':'css-1urpfgu e16867sm0'}).contents #this div's children

        if len(sec_children) > 1: #format 1 in dictionary.com
            define = pron + '\n'
            for child in sec_children[1:]: #iterate through children from element 1
                pos = child.contents[0].text
                define += pos + '\n'

                counter = 1 #numbering the definitions
                for defs in child.contents[1]:
                    define += str(counter) + '. ' + defs.text + '\n'
                    counter += 1

                if 'SEE MORESEE LESS' in define:
                    define = define.replace('SEE MORESEE LESS','')
                print(clipboard + ' defined.')
                show_notif(word, define) #display notification
                define = ''
        else: #format 2 in dictionary.com
            define = ''
            sec_children = soup.find('div', {'class':'default-content'}).contents #format 2's div's children
            for child in sec_children[1:]: #iterate through children
                pos = child.contents[0].text
                define += pos + '\n'

                counter = 1 #numbering the definitions
                for defs in child.contents[1]:
                    define += str(counter) + '. ' + defs.text + '\n'
                    counter += 1

                if 'SEE MORESEE LESS' in define:
                    define = define.replace('SEE MORESEE LESS','')
                print(clipboard + ' defined.')
                show_notif(word, define) #display notification
                define = ''

def on_activate():
    controller = Controller()

    #simulate key presses to copy to clipboard
    controller.press(Key.ctrl)
    controller.press('c')
    controller.release(Key.ctrl)
    controller.release('c')
    print('Copied to clipboard.')
    global clipboard
    clipboard = pyperclip.paste() #returns contents of clipboard
    print('Clipboard extracted.')

    #scraping the definition
    url = 'https://www.dictionary.com/browse/'+clipboard
    try:
        global page
        global soup
        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.text, 'lxml')
        print('Soup ready.')
        decision()
    except Exception:
        show_notif('Error','Request did not through. Check your internet connection.')



if __name__ == '__main__':
    combo = '<alt>+t' #change this if you want something else
    try:
        with keyboard.GlobalHotKeys({combo: on_activate}) as h:
            h.join()
    except KeyboardInterrupt:
        print('\nProgram terminated')
