# Free Simple PDF Combiner
# Ben Gullason

from datetime import datetime
from pathlib import Path

# https://github.com/mstamy2/PyPDF2
import PyPDF2
# https://pysimplegui.readthedocs.io/en/latest/
import PySimpleGUI as simple_gui
import logging
import base64

simple_gui.theme('Light Grey 1')  # adds a theme to the GUI

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("LOGS.log"),
    ]
)
logger = logging.getLogger()


# Variables
remove_full_path = False
listbox_names_str = []
output_path_str = ''
listbox_path_selected = ''
log_width = 60
log_counter = 0
logs_enabled = False


def split(path, name_of_split):
    pdf = PyPDF2.PdfFileReader(path)
    for page in range(pdf.getNumPages()):
        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))

        output = f'{name_of_split}_({page}).pdf'
        with open(output, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)


def merge_pdfs(paths, output):
    pdf_writer = PyPDF2.PdfFileWriter()

    for path in paths:
        pdf_reader = PyPDF2.PdfFileReader(path)
        for page in range(pdf_reader.getNumPages()):
            # Add each page to the writer object
            pdf_writer.addPage(pdf_reader.getPage(page))

    # Write out the merged PDF
    with open(output, 'wb') as out:
        pdf_writer.write(out)


def _log(new_log_line):
    now = datetime.now()
    global log_counter
    message = f'[{log_counter}][' + now.strftime("%d/%m/%Y %H:%M:%S") + ']: ' + new_log_line
    window['-LOG-'].print(message, autoscroll=True)
    if logs_enabled:  # if logs are not enabled, write to log file
        logger.info(message)
    log_counter += 1


def _add_file(file_name, remove_path):
    if remove_path:
        file_name = Path(file_name).name
    listbox_names_str.append(file_name)
    window['-LIST-'].update(values=listbox_names_str)


# GUI Layout Columns
col1 = [
    [
        simple_gui.Text(key='-LABEL-',
                        text='Add PDF files to combine them. \nUse the controls to rearrange or remove files.')],

    [
        simple_gui.Text(text='Add Files:', size=(8, 1)),
        simple_gui.Input(key='-FILE-', visible=False, enable_events=True),
        simple_gui.FilesBrowse(file_types=(('PDF', '*.pdf'),)),
        simple_gui.Button('Remove All')],
    [
        simple_gui.Checkbox(key='-SHOWLOG-', default=False, text='Show log panel', enable_events=True),
        simple_gui.Checkbox(key='-ENABLELOGS-', default=False, text='Write to log file', enable_events=True)],
    [
        simple_gui.Listbox(key='-LIST-', values=listbox_names_str, size=(log_width, None),
                           select_mode="LISTBOX_SELECT_MODE_SINGLE", horizontal_scroll=True, enable_events=True,
                           expand_y=True, expand_x=True)],
    [
        simple_gui.Text("Move Selected Up or Down"),
        simple_gui.Button('↑'),
        simple_gui.Button('↓'),
        simple_gui.Button('Remove Selected'),
        simple_gui.Button('Exit')],
    [
        simple_gui.Input(key='-FILE_OUT-', visible=False, enable_events=True),
        simple_gui.FileSaveAs(button_text="Merge and Save As...", key='-SAVEBTN-', disabled=True,
                              file_types=(('PDF', '*.pdf'),)),
        simple_gui.Input(key='-SPLIT_FILE-', visible=False, enable_events=True),
        simple_gui.FileBrowse(button_text="Browse and Split...", key='-SPLIT-', disabled=False,
                              file_types=(('PDF', '*.pdf'),))]
]

col2 = [
    [simple_gui.Text('Application Log', key='-LOGTITLE-')],
    [simple_gui.Multiline(default_text='', disabled=True, autoscroll=True, do_not_clear=True, echo_stdout_stderr=True,
                          key='-LOG-', size=(log_width, 0), enable_events=True, expand_y=True, expand_x=False)]]

col_layout = [
    [
        simple_gui.Column(col1, element_justification='left'),
        simple_gui.Column(col2, key='-LOGCOL-', visible=False, element_justification='center',
                          vertical_alignment='top', expand_y=True, expand_x=False)]]

# Create the window
window = simple_gui.Window('Free Simple PDF Combiner', col_layout)

# Display and interact with the Window using an Event Loop
while True:

    # See if user wants to quit or window was closed
    event, values = window.read()
    if event in (simple_gui.WIN_CLOSED, 'Exit'):
        break

    # Show and hide the log when the show log checkbox is clicked
    if event == '-SHOWLOG-':
        if values['-SHOWLOG-']:
            window['-LOGCOL-'].update(visible=True)
            # window['-LOGCOL-'].set_size(size=(None, None))
            window['-LOGCOL-'].expand(False, True, False)
            # window['-LOG-'].set_size(size=(log_width, None))
            window['-LOG-'].expand(True, True, True)
            window.Refresh()
        else:
            window['-LOGCOL-'].update(visible=False)
            window.refresh()

    # Enable or disable logging
    if event == '-ENABLELOGS-':
        logs_enabled = values['-ENABLELOGS-']

    # Get the selected items in the listbox
    if event == '-LIST-':
        if len(window['-LIST-'].get()) > 0:
            listbox_path_selected = window['-LIST-'].get()[0]
            _log("Selection: " + listbox_path_selected)  # Logging

    # Get the file selected and add its path to the listbox
    if event == '-FILE-' and values['-FILE-'] != '':
        file_list_string = values['-FILE-']
        file_list = file_list_string.split(';')
        for new_file in file_list:
            if not listbox_names_str.__contains__(new_file) and new_file != '':
                _add_file(new_file, remove_full_path)
                window['-SAVEBTN-'].update(disabled=False)
                _log("Added: " + new_file)  # Logging
            else:
                _log("Already added: " + str(new_file))  # Logging

    # Remove all files
    if event == 'Remove All':
        if len(listbox_names_str) == 0:
            _log("No Files To Remove")  # Logging
        else:
            listbox_path_selected = ''
            listbox_names_str.clear()
            window['-LIST-'].update(values=listbox_names_str)
            window['-SAVEBTN-'].update(disabled=True)
            _log("Removed All Files")  # Logging

    # Remove the selected file path(s) from the listbox
    if event == 'Remove Selected':
        if listbox_path_selected == '':
            _log("Nothing Selected")  # Logging
        else:
            index_of_selected = window['-LIST-'].get_indexes()[0]
            listbox_names_str.remove(listbox_path_selected)
            window['-LIST-'].update(values=listbox_names_str)
            _log("Removed: " + listbox_path_selected)  # Logging
            listbox_path_selected = ''
            window['-FILE-'].update(value="")
            if len(listbox_names_str) == 0:
                window['-SAVEBTN-'].update(disabled=True)
            else:
                if index_of_selected > 0:
                    index_of_selected -= 1
                window['-LIST-'].update(set_to_index=index_of_selected)
                listbox_path_selected = window['-LIST-'].get()[0]

    # Move selected listbox item up one position
    if event == '↑' and len(listbox_names_str) > 1 and listbox_path_selected != '':
        index = listbox_names_str.index(listbox_path_selected)
        if index > 0:
            moving_value = listbox_names_str.pop(index)
            listbox_names_str.insert(index - 1, moving_value)
            window['-LIST-'].update(values=listbox_names_str)
            window['-LIST-'].set_value(moving_value)
            _log("Move Up: " + moving_value)  # Logging

    # Move selected listbox item down one position
    if event == '↓' and len(listbox_names_str) > 1 and listbox_path_selected != '':
        index = listbox_names_str.index(listbox_path_selected)
        if index < len(listbox_names_str) - 1:
            moving_value = listbox_names_str.pop(index)
            listbox_names_str.insert(index + 1, moving_value)
            window['-LIST-'].update(values=listbox_names_str)
            window['-LIST-'].set_value(moving_value)
            _log("Move Down: " + moving_value)  # Logging

    # Merge files in the listbox into one PDF file
    if event == '-FILE_OUT-' and len(listbox_names_str) > 0:
        new_file_name = values['-FILE_OUT-']

        if new_file_name == '':
            _log("No file selected")  # Logging
        else:
            # Use the merge_pdfs function from the pdf_merge.py file
            merge_pdfs(listbox_names_str, new_file_name)
            _log("Merged PDFs to: " + new_file_name)  # Logging

    # Split selected file in the listbox into multiple PDF files
    if event == '-SPLIT_FILE-' and values['-SPLIT_FILE-'] != '':
        split_file = values['-SPLIT_FILE-']
        parent_path = str(Path(split_file).parent)
        output_path = split_file[0:len(split_file) - 4]
        split(split_file, output_path)
        _log("Split PDF to: " + parent_path)  # Logging

# Finish up by removing from the screen
window.close()
