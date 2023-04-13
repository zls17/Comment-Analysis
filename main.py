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
from nltk.sentiment import SentimentIntensityAnalyzer
import pyqtgraph as pg
from PyQt5.QtChart import (QChart, QChartView, QPieSeries, 
                           QPieSlice)
from PyQt5.QtGui import QPainter
import random
# from nltk.sentiment import SentimentIntensityAnalyzer


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):

        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
            

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

    def barChartGraph(self):
        window = MainWindow()
        plot = pg.plot()
        y = [self.positive_count, self.negative_count, self.neutral_count]
        x = [1, 2, 3]
        bargraph = pg.BarGraphItem(x = x, height = y, width = 0.5, brush = 'g')
        plot.addItem(bargraph)
        plot.setBackground('w')
        plot.setLabel('left', "Number of Comments")
        window.show()



    def pieChartGraph(self):
        series = QPieSeries()
        series.append("Positive", self.positive_count)
        series.append("Negative", self.negative_count)
        series.append("Neutral", self.neutral_count)

        slice = QPieSlice()
        positiveSlice = QPieSlice()
        positiveSlice = series.slices()[0]
        positiveSlice.setLabelVisible(True)

        negativeSlice = QPieSlice()
        negativeSlice = series.slices()[1]
        negativeSlice.setLabelVisible(True)

        neutralSlice = QPieSlice()
        neutralSlice = series.slices()[2]
        neutralSlice.setLabelVisible(True)
        chart = QChart()
        
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle("Comment Pie Chart")
        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
        self.chartBack = QPushButton("Back")
        layout = QVBoxLayout()
        layout.addWidget(chartview)
        layout.addWidget(self.chartBack)
        widget = QWidget()
        widget.setLayout(layout)
        self.chartBack.pressed.connect(self.sentiment)
        self.setCentralWidget(widget)
        
        # self.setCentralWidget(chartview)

    def sentiment(self):
        sia = SentimentIntensityAnalyzer()
        self.positive_count = 0
        self.negative_count = 0
        self.neutral_count = 0
        for comment in self.comments:
            if sia.polarity_scores(comment)['compound'] >= 0.05:
                self.positive_count += 1
            elif sia.polarity_scores(comment)['compound'] <= -0.05:
                self.negative_count += 1
            else:
                self.neutral_count += 1
            
        loadUi("sentimentUI.ui", self)
        self.totalComments.setText(str(len(self.comments)))
        self.positiveComments.setText(str(self.positive_count))
        self.negativeComments.setText(str(self.negative_count))
        self.neutralComments.setText(str(self.neutral_count))
        
        if self.positive_count > 2 * self.negative_count:
            self.descriptionLabel.setText("Overall, the video was well received.")
        elif self.negative_count > self.positive_count:
            self.descriptionLabel.setText("People did not like this video!")
        else:
            self.descriptionLabel.setText("It wasn't good but not bad either")

        self.backButton.pressed.connect(self.youtubeAnalysis)
        self.pieChart.pressed.connect(self.pieChartGraph)
        self.barGraph.pressed.connect(self.barChartGraph)

        

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
            self.homeButton = QPushButton("Home")
            layout = QVBoxLayout()
            layout.addWidget(self.table)
            layout.addWidget(self.saveButton)
            layout.addWidget(self.analyseButton)
            layout.addWidget(self.homeButton)
            widget = QWidget()
            widget.setLayout(layout)
            self.saveButton.pressed.connect(self.save)
            self.analyseButton.pressed.connect(self.sentiment)
            self.homeButton.pressed.connect(self.youtubeUI)
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

app = QApplication([])
window = MainWindow()
app.exec()
