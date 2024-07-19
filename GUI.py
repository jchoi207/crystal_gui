from PySide6.QtWidgets import (QApplication,
                               QWidget,
                               QInputDialog,
                               QLineEdit,
                               QFileDialog,
                               QPushButton,
                               QVBoxLayout,
                               QHBoxLayout,
                               QLabel,
                               QGridLayout,
                               QFormLayout
                               )
from PySide6.QtCore import QTimer, QEventLoop, Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6 import QtGui

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

import numpy as np

import h5py
import sys
import shutil
import os
import time

matplotlib.use('Qt5Agg')
make_copy = False

class FigurePlot(QWidget):
    def __init__(self, parent=None, width=5, height=4, dpi=200):
        super(FigurePlot, self).__init__(parent)

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111)

        self.make_copy = False
        self.path = None
        self.curr_idx = 0
        self.all_patterns = None
        self.len = 0
        self.output = ''
        self.min_norm = 3
        self.max_norm = 99

        self.ui()

    def ui(self, *args, **kwargs):
        # INSTRUCTIONS
        self.curr_file = QLabel(
            "Please browse for a file to display\n\nNote, selecting 'Trash', will delete the \nimage you've currently selected. \n\nToggling 'Copy File' before browsing for a pattern\n will make a copy of the file. \n\n You can adjust the input intensities to change the contrast.", self)
        self.curr_file.adjustSize()
        self.curr_file.setStyleSheet(
            '''
            color: #E8E8E8;
            background-color: #2C2C2C;
            margin: 20px;
            padding: 20px;
            width: 100px;
            height: 120px;
            border: 3px solid #A0A0A0;
            border-radius: 10px;
            font-size: 13pt;
            '''
        )
        self.curr_file.setFixedSize(500, 300)

        # TERMINAL
        self.terminal = QLabel(f">>{self.output}")
        self.terminal.setStyleSheet(
            '''
            color: #E8E8E8;
            background-color: #2C2C2C;
            margin: 20px;
            padding: 20px;
            width: 100px;
            height: 120px;
            border: 3px solid #A0A0A0;
            border-radius: 10px;
            font-size: 13pt;
            '''
        )
        self.terminal.setFixedSize(500, 150)

        text_layout = QVBoxLayout()
        text_layout.addWidget(self.curr_file)
        text_layout.addWidget(self.terminal)

        # TOGGLE
        self.button0 = QPushButton('Copy File')
        self.button0.toggled.connect(self.copy_file)
        self.button0.setFixedSize(100, 40)
        self.button0.setCheckable(True)
        self.button0.setStyleSheet(  # green
            '''
            background: #2ed573;
            color: white;
            border: 1px solid white;
            border-radius: 5px;
            '''
        )

        toggle_layout = QGridLayout()
        toggle_layout.addWidget(self.button0, 0, 0)

        # VMIN and VMAX INPUT FIELDS

        self.min_line_edit = QLineEdit(parent=self)
        self.min_line_edit.setValidator(QIntValidator())
        self.min_line_edit.setText("3")

        self.max_line_edit = QLineEdit(parent=self)
        self.max_line_edit.setValidator(QIntValidator())
        self.max_line_edit.setText("99")
        
        self.min_norm = np.clip(int(self.min_line_edit.text()), 0, 100)
        self.max_norm = np.clip(int(self.max_line_edit.text()), 0, 100)

        self.min_line_edit.setStyleSheet(
            '''
            min-width: 125px;
            max-width: 125px;
            background: light-gray;
            margin-right:+25px;
            '''
        )
        self.max_line_edit.setStyleSheet(
            '''
            min-width: 125px;
            max-width: 125px;
            background: light-gray;
            margin-right:+25px;
            '''
        )

        edit_layout = QGridLayout()
        # Adjust horizontal spacing as needed
        edit_layout.setHorizontalSpacing(5)

        min_label = QLabel(parent=self, text="Normalized min [0-100]")
        max_label = QLabel(parent=self, text="Normalized max [0-100]")

        # Adding some negative margin to the right of the labels
        min_label.setStyleSheet("margin-right: +25px;")
        max_label.setStyleSheet("margin-right: +25px;")

        edit_layout.addWidget(
            min_label, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        edit_layout.addWidget(self.min_line_edit, 0, 1,
                              alignment=Qt.AlignmentFlag.AlignLeft)
        edit_layout.addWidget(
            max_label, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        edit_layout.addWidget(self.max_line_edit, 1, 1,
                              alignment=Qt.AlignmentFlag.AlignLeft)

        # BUTTONS
        self.button1 = QPushButton('Browse')
        self.button1.clicked.connect(self.open_file)
        self.button2 = QPushButton('Plot')
        self.button2.clicked.connect(self.init_graph)
        self.button3 = QPushButton('<-')
        self.button3.clicked.connect(lambda: self.next_graph(False))
        self.button4 = QPushButton('->')
        self.button4.clicked.connect(lambda: self.next_graph(True))
        self.button5 = QPushButton('Close App')
        self.button5.clicked.connect(self.close_mainwindow)
        self.button6 = QPushButton('Trash')
        self.button6.clicked.connect(self.delete_graph)

        buttons = [self.button1, self.button2, self.button3,
                   self.button4, self.button5, self.button6]
        for button in buttons:
            button.setFixedSize(100, 40)
            button.setStyleSheet(  # blue
                '''
                background: #1e90ff;
                color: white;
                border: 1px solid white;
                border-radius: 5px;
                '''
            )

        button_layout = QGridLayout()
        button_layout.addWidget(self.button1, 0, 0)
        button_layout.addWidget(self.button2, 0, 1)
        button_layout.addWidget(self.button3, 1, 0)
        button_layout.addWidget(self.button4, 1, 1)
        button_layout.addWidget(self.button5, 2, 0)
        button_layout.addWidget(self.button6, 2, 1)
        self.button5.setStyleSheet(
            '''
            background: #ff4757;
            color: white;
            border: 1px solid white;
            border-radius: 5px;
            '''
        )
        self.button6.setStyleSheet(  # red
            '''
            background: #ff4757;
            color: white;
            border: 1px solid white;
            border-radius: 5px;
            '''
        )
        # COMBINING UI LAYOUTS
        ui_layout = QVBoxLayout()
        ui_layout.addLayout(text_layout)
        ui_layout.addLayout(toggle_layout)
        ui_layout.addLayout(edit_layout)
        ui_layout.addLayout(button_layout)

        # COMBINING UI WITH CANVAS
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(ui_layout)

        self.setLayout(main_layout)
        # self.setLayout(button_layout)
        # self.setLayout

    def open_file(self, *args, **kwargs):
        self.print_terminal(f"Browsing")
        opts = QFileDialog.Options()
        opts |= QFileDialog.DontUseNativeDialog
        file, _ = QFileDialog.getOpenFileName(self,
                                              "QFileDialog.getOpenFileName()",
                                              "", "All Files (*);;Python Files (*.py)",
                                              options=opts)
        self.path = file

        if self.make_copy:

            version = 0
            trash_path = os.path.join(os.path.dirname(self.path), "trash")

            if not os.path.exists(trash_path):
                os.makedirs(trash_path)

            split_path = os.path.basename(self.path).split(".hp")[0]
            copy_path = os.path.join(trash_path, split_path + "_copy_0.hp")
            while os.path.exists(copy_path):
                version += 1
                copy_path = os.path.join(
                    trash_path, split_path + f"_copy_{version}.hp")

            copy_path = os.path.join(
                trash_path, split_path + f"_copy_{version}.hp")
            self.print_terminal(f"Making a copy at: {
                                os.path.relpath(copy_path)}")
            shutil.copy(file, copy_path)
            self.delay(3)

        self.print_terminal(f"Opened file at: {os.path.relpath(
            self.path)}\n>> Click 'Plot' to view")

    def copy_file(self):
        self.make_copy = not self.make_copy
        self.print_terminal(f"Toggle Copy: {self.make_copy}")

    def init_graph(self, *args, **kwargs):
        if self.path:
            with h5py.File(self.path, 'a') as f:
                self.all_patterns = f['diffraction']['micrograph'][:]
                self.len = len(self.all_patterns)
                self.plot_graph()
                self.print_terminal(f"Plotted {os.path.relpath(
                    self.path)}\n>> Number of patterns: {self.len}\n>> Input Intensities{sorted([self.min_norm, self.max_norm])}")

    def plot_graph(self, *args, **kwargs):

        self.min_norm = np.clip(int(self.min_line_edit.text()), 0, 100)
        self.max_norm = np.clip(int(self.max_line_edit.text()), 0, 100)
        
        if self.len > 0:
            self.curr_pattern = self.all_patterns[self.curr_idx]
            self.axes.clear()

            vmin = np.percentile(self.curr_pattern, min(
                self.min_norm, self.max_norm))
            vmax = np.percentile(self.curr_pattern, max(
                self.min_norm, self.max_norm))
            self.axes.imshow(self.curr_pattern, cmap='gray',
                             vmin=vmin, vmax=vmax)
            self.axes.set_title(f" Pattern {self.curr_idx + 1}/{self.len}")
            self.canvas.draw()

    def next_graph(self, next: bool = None, *args, **kwargs):
        self.min_norm = np.clip(int(self.min_line_edit.text()), 0, 100)
        self.max_norm = np.clip(int(self.max_line_edit.text()), 0, 100)
        if next is not None:
            if next:
                self.curr_idx += 1
                if self.curr_idx == self.len:
                    self.curr_idx = 0
                self.print_terminal(f"1 forward\n>> Pattern {
                                    self.curr_idx+1}/{self.len}\n>> Input Intensities{sorted([self.min_norm, self.max_norm])}")

            else:
                self.curr_idx -= 1
                if self.curr_idx == -1:
                    self.curr_idx = self.len - 1
                self.print_terminal(f"1 back\n>> Pattern {
                                    self.curr_idx+1}/{self.len}\n>> Inputs Intensities{sorted([self.min_norm, self.max_norm])}")
            self.plot_graph()

    def close_mainwindow(self):
        self.terminal.setText(">> Closing Application :)")
        self.delay(0.5)
        main_window = self.window()
        if isinstance(main_window, QMainWindow):
            main_window.close()

    def delete_graph(self, *args, **kwargs):
        if self.len > 0:
            with h5py.File(self.path, 'a') as f:
                patterns = f['diffraction']['micrograph'][:]
                deleted_index = self.curr_idx
                new_data = np.delete(patterns, self.curr_idx, axis=0)
                del f['diffraction']['micrograph']
                f.create_dataset('diffraction/micrograph', data=new_data)
                self.all_patterns = new_data
                self.len = len(self.all_patterns)
                if self.curr_idx >= self.len:
                    self.curr_idx = 0
                self.print_terminal(
                    f"Deleted image at index {deleted_index+1}")
                self.plot_graph()

    def delay(self, seconds):
        timer = QTimer()
        timer.setSingleShot(True)
        loop = QEventLoop()
        timer.timeout.connect(loop.quit)
        timer.start(seconds * 1000)
        loop.exec()

    def print_terminal(self, message, seconds=0.025):
        self.output = f">> {message}"
        print(self.output)
        self.delay(seconds)
        self.terminal.setText(">>")
        self.delay(seconds)
        self.terminal.setText(self.output)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.title = "Plot"
        self.setWindowTitle(self.title)
        self.plot = FigurePlot(self, width=15, height=15, dpi=200)
        self.setCentralWidget(self.plot)


app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

w = MainWindow()
w.show()
app.exec()