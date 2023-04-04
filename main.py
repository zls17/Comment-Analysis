from PyQt5.QtWidgets import (QApplication, QPushButton, QMainWindow,
                             QVBoxLayout, QWidget, QGridLayout, QLabel,
                             QLineEdit)
from PyQt5.uic import loadUi
from googleapiclient.discovery import build
import pandas as pd 
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import pandas as pd


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
        # layout.addWidget(self.orLabel, 1, 0)
        # layout.addWidget(self.channelLabel, 2, 0)
        # layout.addWidget(self.channelEntry, 2, 1)
        # layout.addWidget(self.videoTitle, 3, 0)
        # layout.addWidget(self.videoTitleEntry, 3, 1)
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
            comments = []
            for i in range(self.number):
                comments.append(response["items"][i]["snippet"]["topLevelComment"]["snippet"]["textOriginal"])
            df = pd.DataFrame({"comments": comments})
            print(df)

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
