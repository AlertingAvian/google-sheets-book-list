from time import time
from typing import List

import PySimpleGUI as sg
import cv2

import exceptions
import isbn
import scanner
import sheet
from models import BookData


def main_layout() -> list:
    column_0 = [[sg.Image(key='image_player', size=(177, 100), right_click_menu=['', ['Change Device']])]]
    column_1 = [[sg.Text('Title'), sg.HSeparator(color='#24292e'), sg.InputText(text_color='black',
                                                                                key='title_box', disabled=True)],
                [sg.Text('Author(s) '), sg.HSeparator(color='#24292e'), sg.InputText(text_color='black',
                                                                                     key='author_box', disabled=True)],
                [sg.Text('Year'), sg.HSeparator(color='#24292e'), sg.InputText(text_color='black',
                                                                               key='year_box', disabled=True)],
                [sg.Text('Publishers'), sg.HSeparator(color='#24292e'), sg.InputText(text_color='black',
                                                                                     key='publishers_box',
                                                                                     disabled=True)],
                [sg.Text('ISBN'), sg.HSeparator(color='#24292e'), sg.InputText(text_color='black',
                                                                               key='isbn_box', disabled=True)],
                [sg.Text('Description'), sg.HSeparator(color='#24292e'), sg.Button('Show', key='description_button',
                                                                                   disabled=True)],
                [sg.Text('Notes'), sg.HSeparator(color='#24292e'), sg.Button('Edit', key='notes_button',
                                                                             disabled=True)],
                [sg.Button('Enter', button_color='green', key='enter_button', disabled=True),
                 sg.HSeparator(color='#24292e'), sg.Button('ISBN Lookup', key='lookup_button'),
                 sg.HSeparator(color='#24292e'), sg.Button('Manual', button_color='red', key='manual_button')]]

    layout_array = [[sg.Column(column_0), sg.Column(column_1)]]

    return layout_array


def isbn_search_popup() -> list:
    layout = [[sg.InputText(key="manual_isbn", tooltip="ISBN to lookup", focus=True)],
              [sg.Button("Search", key='search_button')]]
    return layout


def multiline_text_popup(text: str = "") -> list:
    layout = [[sg.Multiline(default_text=text, size=(80, 10))],
              [sg.OK()]]
    return layout


def device_popup():
    devices = video_devices()
    layout = [[sg.Text("Device Index:")],
              [sg.Listbox(devices, size=(10, len(devices)), key='device')],
              [sg.OK()]]
    return layout


def video_devices() -> List[int]:
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr


def event_loop() -> None:
    sg.theme('DarkGrey14')
    window = sg.Window('Book Tracker', main_layout())

    device = 0
    stream = cv2.VideoCapture(device)

    window_timeout = 1000 // 60

    scan_timeout = 0
    scan_timeout_max = 5

    description = ""
    book_data = None
    notes = ""
    manual_mode = False
    _, ws = sheet.open_or_create_sheet()

    image_elem = window['image_player']

    previous_time = time()

    while True:
        current_time = time()
        delta_time = current_time - previous_time

        event, values = window.read(timeout=window_timeout)
        if event in ('Exit', None):
            break

        _, frame = stream.read()

        image = cv2.resize(frame, (177, 100), interpolation=cv2.INTER_AREA)
        img_bytes = cv2.imencode('.ppm', image)[1].tobytes()
        image_elem.update(data=img_bytes)

        scan_result = None

        if scan_timeout <= 0 and not manual_mode:
            scan_result = scanner.decode_barcode(frame)
        elif scan_timeout > 0:
            scan_timeout -= delta_time

        if scan_result and isbn.validate_isbn(str(scan_result[0])):
            scan_timeout = scan_timeout_max
            try:
                book_data = isbn.get_data(str(scan_result[0]))
            except exceptions.NoDataError as e:
                sg.PopupError(e.message + "\nEnter data manually.", title="Error")
            else:
                window['title_box'].update(book_data.Title)
                window['author_box'].update(", ".join(book_data.Authors))
                description = book_data.Description
                notes = ""
                window['year_box'].update(book_data.Year)
                window['publishers_box'].update(book_data.Publisher)
                window['isbn_box'].update(book_data.ISBN)
                window['enter_button'].update(disabled=False)
                window['description_button'].update(disabled=False)
                window['notes_button'].update(disabled=False)

        if event == 'description_button' and not manual_mode:
            sg.popup(description, title="Description", line_width=150)
        elif event == 'enter_button' and book_data and not manual_mode:
            window['title_box'].update("")
            window['author_box'].update("")
            description = ""
            window['year_box'].update("")
            window['publishers_box'].update("")
            window['isbn_box'].update("")
            window['enter_button'].update(disabled=True)
            window['description_button'].update(disabled=True)
            window['notes_button'].update(disabled=True)
            sheet.add_book(ws, book_data, notes)
            notes = ""
            book_data = None
        elif event == 'enter_button' and manual_mode:
            manual_book_data = BookData(Title=values['title_box'],
                                        Authors=list(map(str.strip, values['author_box'].split(','))),
                                        Year=values['year_box'], Publisher=values['publishers_box'],
                                        ISBN=values['isbn_box'], Description=description)
            sheet.add_book(ws, manual_book_data, notes)
            manual_mode = False
            window['title_box'].update("", disabled=True, text_color='black')
            window['author_box'].update("", disabled=True, text_color='black')
            description = ""
            notes = ""
            window['year_box'].update("", disabled=True, text_color='black')
            window['publishers_box'].update("", disabled=True, text_color='black')
            window['isbn_box'].update("", disabled=True, text_color='black')
            window['enter_button'].update(disabled=True)
            window['description_button'].update('Show', disabled=True)
            window['notes_button'].update(disabled=True)
        elif event == 'description_button' and manual_mode:
            popup_window = sg.Window("Description", multiline_text_popup(description))
            event, values = popup_window.read()
            description = values[0]
            popup_window.close()
        elif event == 'manual_button' and not manual_mode:
            manual_mode = True
            window['title_box'].update(disabled=False, text_color='white')
            window['author_box'].update(disabled=False, text_color='white')
            window['year_box'].update(disabled=False, text_color='white')
            window['publishers_box'].update(disabled=False, text_color='white')
            window['isbn_box'].update(disabled=False, text_color='white')
            window['enter_button'].update(disabled=False)
            window['description_button'].update('Edit', disabled=False)
            window['notes_button'].update(disabled=False)
        elif event == 'manual_button' and manual_mode:
            manual_mode = False
            window['title_box'].update("", disabled=True, text_color='black')
            window['author_box'].update("", disabled=True, text_color='black')
            description = ""
            notes = ""
            window['year_box'].update("", disabled=True, text_color='black')
            window['publishers_box'].update("", disabled=True, text_color='black')
            window['isbn_box'].update("", disabled=True, text_color='black')
            window['enter_button'].update(disabled=True)
            window['description_button'].update('Show', disabled=True)
            window['notes_button'].update(disabled=True)
        elif event == 'notes_button':
            popup_window = sg.Window("Notes", multiline_text_popup(notes))
            event, values = popup_window.read()
            notes = values[0]
            popup_window.close()
        elif event == 'Change Device':
            print("Ignore the warnings/error it is probably fine.")
            popup_window = sg.Window("Device Selection", device_popup())
            stream.release()
            event, values = popup_window.read()
            device = int(values['device'][0])
            stream = cv2.VideoCapture(device)
            popup_window.close()
        elif event == 'lookup_button':
            popup_window = sg.Window('ISBN Lookup', isbn_search_popup())
            event, values = popup_window.read()
            if event == 'search_button':
                popup_window.close()
                try:
                    book_data = isbn.get_data(values['manual_isbn'])
                except exceptions.NoDataError as e:
                    sg.PopupError(e.message + "\nVerify ISBN or enter data manually.", title="Error")
                else:
                    window['title_box'].update(book_data.Title)
                    window['author_box'].update(", ".join(book_data.Authors))
                    description = book_data.Description
                    notes = ""
                    window['year_box'].update(book_data.Year)
                    window['publishers_box'].update(book_data.Publisher)
                    window['isbn_box'].update(book_data.ISBN)
                    window['enter_button'].update(disabled=False)
                    window['description_button'].update(disabled=False)
                    window['notes_button'].update(disabled=False)

        previous_time = current_time

    stream.release()
