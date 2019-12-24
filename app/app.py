"""
Created by Cameron Rogers
"""
import csv
import docx
import sys
from os import path
import re
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
# pylint: disable=no-name-in-module
from PySide2.QtUiTools import QUiLoader
# pylint: enable=no-name-in-module
from fuzzywuzzy import process

from graticard_entry import GratiCardEntry
from parser import parse_data_to_graticard_entry, validate_column_map, InvalidColumnMapError
        

def load_ui(ui_file_name):
    ui_file = QtCore.QFile(ui_file_name)
    ui_file.open(QtCore.QFile.ReadOnly)
    loader = QUiLoader()
    return loader.load(ui_file)


class App(QtWidgets.QApplication):
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = MainWindowManager()
        self.main_window.ui.show()


class FileManager:
    def __init__(self, parser_ui):
        self.files = []
        self.parser_ui = parser_ui
        self.parser_idx = 0
        
    def add_file(self, file_paths: list):
        for file_path in file_paths:
            if isinstance(file_path, str) and path.exists(file_path):
                if file_path.split('.')[-1] == "csv":
                    self.files.append(CsvFile(file_path, self.parser_ui))
                elif file_path.split('.')[-1] == "docx":
                    self.files.append(DocxFile(file_path, self.parser_ui))
                else:
                    raise Exception('Unknown file type')
            else:
                raise Exception('Unable to add file')
        
    def remove_file(self, row_index):
        self.files.pop(row_index)
        
    def show_parser(self):
        if self.parser_idx < len(self.files):
            self.files[self.parser_idx].setup_and_show()
            self.parser_idx += 1
        else:
            return

    def connect_processed_signals_of_all_files(self, slot):
        [f.triggered.connect(slot) for f in self.files]

    def __call__(self):
        for f in self.files:
            yield f


class MainWindowManager(QtCore.QObject):
    """Ui wrapper"""
    def __init__(self):
        super().__init__()
        self.ui = load_ui('../ui/mainwindow.ui')
        self.ui.ParseFilesPushButton.clicked.connect(self._show_next_data_parsers)
        self.ui.AddFilePushButton.clicked.connect(self._add_file)
        self.files_model = QtGui.QStandardItemModel()
        self.ui.AddedFilesListView.setModel(self.files_model)
        self.ui.AddedFilesListView.doubleClicked.connect(self._remove_file)
        self.ui.CustomerNameLineEdit.textChanged.connect(self._update_label)
        self.ui.GenerateCsvPushButton.clicked.connect(self.merge)
        
        self.file_manager = FileManager(self.ui)
        self.file_manager.connect_processed_signals_of_all_files(self._show_next_data_parsers)

    def _add_file(self):
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self.ui, "Open File", "~", "Files (*.csv *.docx *.xlsx)")
        self.file_manager.add_file(file_paths)
        self._show_files()
        
    @QtCore.Slot(QtCore.QModelIndex)
    def _remove_file(self, index):
        self.file_manager.remove_file(index.row())
        self._show_files()
            
    def _show_files(self):
        self.files_model.clear()
        for f in self.file_manager():
            item = QtGui.QStandardItem("{} - {}".format(f.get_name(), f.get_status()))
            self.files_model.appendRow(item)

    def _update_label(self):
        new_label = self.ui.CustomerNameLineEdit.text().replace(
            ' ', '_').replace('-', '_')
        if new_label:
            self.ui.CsvFileNameLabel.setText(new_label + '.csv')
        else:
            self.ui.CsvFileNameLabel.setText("")

    def _show_next_data_parsers(self):
        self.file_manager.show_parser()
        self._show_files()
            
    def merge(self):
        csv_entries_dict = None
        docx_entries_dict = None
        for file_ in self.file_manager():
            if file_.status == "Pending":
                return
            if file_.EXTENSION == 'csv':
                csv_entries_dict = {obj.get_recipient_name(): obj for obj in file_.graticard_entry_objects}
            elif file_.EXTENSION == 'docx':
                docx_entries_dict = {obj.get_recipient_name(): obj for obj in file_.graticard_entry_objects}

        if self.ui.CsvFileNameLabel.text() == "":
            self.warn('You need to specify a file')
            return
        
        if csv_entries_dict is None or docx_entries_dict is None:
            self.warn('You need to parse data first')
            return
        
        for csv_entry_name in csv_entries_dict:
            if csv_entry_name in docx_entries_dict:
                csv_entries_dict[csv_entry_name].set_gift(docx_entries_dict[csv_entry_name].get_gift())
                continue
            else:
                all_docx_names = [docx_entry_name for docx_entry_name in docx_entries_dict]
                matched_docx_name, confidence = process.extractOne(csv_entry_name, all_docx_names)
                if confidence > 20:
                    csv_entries_dict[csv_entry_name].set_gift(docx_entries_dict[matched_docx_name].get_gift())

        # with open(self.ui.CsvFileNameLabel.text(), 'w') as csvfile:
        #     csvwriter = csv.writer(csvfile)
        #     csvwriter.writerows(address_list)
        self.info('creating csv - the application will now exit')
        QtCore.QCoreApplication.quit()
        
    def info(self, message):
        flags = QtWidgets.QMessageBox.StandardButton.Ok
        QtWidgets.QMessageBox.information(self.ui, "Information", message, flags)
        
    def warn(self, message):
        flags = QtWidgets.QMessageBox.StandardButton.Ok
        QtWidgets.QMessageBox.warning(self.ui, "Warning", message, flags)


class AbstractFileHandler(QtCore.QObject):
    COMBO_BOX_OPTIONS = ["",
                         "Name",
                         "Street Address",
                         "City State Postal Code",
                         "Address Line 1",
                         "Address Line 2",
                         "City",
                         "State",
                         "Postal Code",
                         "Gift"]
    
    processed = QtCore.Signal()

    def __init__(self, file_path: str, ui: QtWidgets.QWidget):
        super().__init__()
        self.path = Path(path.abspath(file_path))
        self.graticard_entry_objects = []
        self.data = []
        self.status = "Pending"
        self.ui = ui
        
    def setup_and_show(self):
        self.ui.FileParserGroupBox.setTitle(self.get_name())

        # # Setup table
        # layout = QtWidgets.QHBoxLayout()
        # self.ui.ParserTableWidget = QtWidgets.QTableWidget()
        # self.ui.ParserTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # layout.addWidget(self.ui.ParserTableWidget)
        # self.ui.widget_1.setLayout(layout)
        
        # Connect buttons
        self.ui.RemovePushButton.clicked.connect(self.remove_selected_rows)
        self.ui.ParsePushButton.clicked.connect(self.parse)

        self._load_data()
        self._populate_table()
        
    def get_name(self):
        return self.path.name
    
    def get_status(self):
        return self.status
    
    def parse(self):
        column_map = self._get_column_map()
        try:
            validate_column_map(column_map)
        except InvalidColumnMapError as err:
            print('Falied validation - Popup thing here: {}'.format(err))
            return
            
        self.graticard_entry_objects = parse_data_to_graticard_entry(self.data,
                                                                     column_map)
        for obj in self.graticard_entry_objects:
            obj.parse_address()
        self.status = "Complete"
        self._destroy()
        self.processed.emit()
        
    def _load_data(self):
        # Method should be set by the inherited class
        pass
    
    def _destroy(self):
        self.ui.ParserTableWidget.clear()
        self.ui.ParserTableWidget.setRowCount(0)
        self.ui.ParserTableWidget.setColumnCount(0)

    def _populate_table(self):
        if self.data == []:
            return
        self.row_count = len(self.data)
        self.column_count = len(self.data[0])
        self.ui.ParserTableWidget.setRowCount(self.row_count+1)
        self.ui.ParserTableWidget.setColumnCount(self.column_count)

        for j in range(self.column_count):
            cb = QtWidgets.QComboBox()
            cb.addItems(self.COMBO_BOX_OPTIONS)
            self.ui.ParserTableWidget.setCellWidget(0, j, cb)

        for i, row in enumerate(self.data):
            for j, col in enumerate(row):
                self.ui.ParserTableWidget.setItem(i+1, j, QtWidgets.QTableWidgetItem(col))
            if i == self.ui.ParserTableWidget.rowCount():
                break

    def remove_selected_rows(self):
        for r in self.ui.ParserTableWidget.selectedRanges():
            for row in range(r.topRow(), r.bottomRow()+1):
                self.data.pop(row-1)
        self._populate_table()

    def _get_column_map(self):
        """Requires that the name be found and optionally the address and gifts"""
        column_map = [None for j in range(self.column_count)]
        for column_index, _ in enumerate(column_map):
            combo_box = self.ui.ParserTableWidget.cellWidget(0, column_index)
            column_map[column_index] = combo_box.currentText()
        return column_map


class CsvFile(AbstractFileHandler):
    EXTENSION = 'csv'
    def __init__(self, file_path: str, ui: QtWidgets.QWidget):
        super().__init__(file_path, ui)
        
    def _load_data(self):
        with open(self.path.absolute(), 'r', encoding='latin-1') as fh:
            self.data = [row for row in csv.reader(fh)]


class DocxFile(AbstractFileHandler):
    EXTENSION = 'docx'
    
    RULES = [re.compile(r'(.*) -- (.*)'),
             re.compile(r'(.*) (\$.*)')]

    def __init__(self, file_path: str, ui: QtWidgets.QWidget):
        super().__init__(file_path, ui)
        
    def _load_data(self):
        document = docx.Document(self.path.absolute())
        for paragraph in document.paragraphs:
            temp_data = "".join([run.text for run in paragraph.runs])
            if temp_data == "":
                continue
            for rule in self.RULES:
                if rule.match(temp_data) is not None:
                    match = rule.match(temp_data)
                    temp_data = [match.group(1), match.group(2)]
                    break
            self.data.append(temp_data)


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = App(sys.argv)
    sys.exit(app.exec_())
