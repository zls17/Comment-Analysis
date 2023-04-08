from PyQt5.QtWidgets import (QApplication, QPushButton, QMainWindow,
                             QVBoxLayout, QWidget, QGridLayout, QLabel,
                             QLineEdit)
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from googleapiclient.discovery import build
import pandas as pd 
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import pandas as pd
import csv


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):

        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

        # if role == Qt.ItemDataRole.FontRole:
        #     return QFont("Arial", 18)

    def rowCount(self, index):
        return self._data.shape[0]
    
    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            if  orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comment Analyser")
        layout = QVBoxLayout()
        self.redditButton = QPushButton("Reddit")
        self.youtubeButton = QPushButton("Youtube")
        self.twitterButton = QPushButton("Twitter")
        layout.addWidget(self.redditButton)
        layout.addWidget(self.youtubeButton)
        layout.addWidget(self.twitterButton)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.youtubeButton.clicked.connect(self.youtubeUI)
        self.show()
    
    def youtubeUI(self):
        loadUi("youtubeUI.ui", self)
        layout = QGridLayout()
        self.linkLabel = QLabel("Enter the video link")
        self.linkEntry = QLineEdit()
        self.orLabel = QLabel("OR")
        self.channelLabel = QLabel("Enter channel name")
        self.channelEntry = QLineEdit()
        self.videoTitle = QLabel("Enter video title")
        self.videoTitleEntry = QLineEdit()
        self.analyseButton = QPushButton("Show Comments")
        self.numberCommentsLabel = QLabel("Enter Number of Comments to retrieve")
        self.numberCommentsEntry = QLineEdit()
        self.linkEntry.textChanged.connect(self.getYoutubeLink)
        self.analyseButton.clicked.connect(self.youtubeAnalysis)
        self.numberCommentsEntry.textChanged.connect(self.getNumberComments)
        layout.addWidget(self.linkLabel, 0, 0)
        layout.addWidget(self.linkEntry, 0, 1)
        layout.addWidget(self.numberCommentsLabel, 1, 0)
        layout.addWidget(self.numberCommentsEntry, 1, 1)
        layout.addWidget(self.analyseButton, 2, 0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()

    def getNumberComments(self, number):
        self.number = int(number)
        

    def getYoutubeLink(self, link):
        self.videoLink = link
    
    def save(self):
        with open("output.txt", 'w') as file:
            for comment in self.comments:
                file.write(f"{comment}\n")


    def youtubeAnalysis(self):
        load_dotenv()
        API_KEY = os.getenv("API_KEY")

        youtube = build("youtube", "v3", developerKey = API_KEY)

        def comment_threads(videoID, to_csv=False):
            request = youtube.commentThreads().list(
                part = 'snippet',
                videoId = videoID,
                maxResults = self.number
            )
            response = request.execute()
            self.comments = []
            for i in range(self.number):
                self.comments.append(response["items"][i]["snippet"]["topLevelComment"]["snippet"]["textOriginal"])
            pd.options.display.max_colwidth = 100
            self.df = pd.DataFrame(data = self.comments, columns = ["Comments"])
            self.table = QtWidgets.QTableView()
            self.model = TableModel(self.df)
            self.table.setModel(self.model)
            self.table.setColumnWidth(0, 10000)
            self.saveButton = QPushButton("Save")
            self.analyseButton = QPushButton("Analyse")
            layout = QVBoxLayout()
            layout.addWidget(self.table)
            layout.addWidget(self.saveButton)
            layout.addWidget(self.analyseButton)
            widget = QWidget()
            widget.setLayout(layout)
            self.saveButton.pressed.connect(self.save)
            self.setCentralWidget(widget)



        def url_to_id(url):
            #https://www.youtube.com/watch?v=SwSbnmqk3zY&ab_channel=techTFQ
            for piece in url.split("/"):
                if "watch" in piece:
                    for el in piece.split("="):
                        if "watch" in el:
                            continue
                        else:
                            for e in el.split("&"):
                                if "channel" in e:
                                    continue
                                else:
                                    return e


            # print(url_to_id("https://www.youtube.com/watch?v=XTjtPc0uiG8&ab_channel=SamuelChan"))

        comment_threads(url_to_id(self.videoLink))




    # def twitterUI(self):
    #     loadUi("twitterUI.ui", self)
    #     layout = QGridLayout()
    #     self.



app = QApplication([])
window = MainWindow()
app.exec()
