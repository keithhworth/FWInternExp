## This is a testing of a working, basic GUI found online; updates will need to be made to process files and methods together to produce updates

import PySimpleGUI as sg

sg.change_look_and_feel('DarkBlue')  # Add a touch of color
# All the stuff inside your window.
layout = [[sg.Text('\nUpdate the file name with the appropriate date:', font=('Montserrat', 18))],
          [sg.InputText('CheckedCompanies_*insert correct date*.csv', size=(40, 3), font=('Montserrat', 16))],
          [sg.Text('')],
          [sg.Button('Run', size=(5, 1), font=('Montserrat', 12)), sg.Button('Cancel', size=(5, 1), font=('Montserrat', 12))],
          [sg.Text('')]
          ]

# Create the Window
window = sg.Window('Dictionary Generator', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Cancel'):  # if user closes window or clicks cancel
        break
    print('You entered ', values[0])

window.close()

