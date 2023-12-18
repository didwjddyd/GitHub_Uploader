import sys
import os
import GitUploder

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi

id = ""
pw = ""

class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("GUI.ui", self)
        
        self.Browse.clicked.connect(self.BrowseFolder)
        self.Add.clicked.connect(self.AddToTable)
        self.Delete.clicked.connect(self.DeleteLine)
        self.Upload.clicked.connect(self.UploadFolder)
        self.Set.clicked.connect(self.SetUserInfo)
        self.Reset.clicked.connect(self.ResetUserInfo)
        
    def BrowseFolder(self):
        FolderName = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.expanduser("~/Desktop"))
        self.FolderPath.setText(FolderName)
        
    def AddToTable(self):
        row = self.FolderList.rowCount()
        
        folderPathText = self.FolderPath.text()
        repoNameText = self.RepositoryName.text()
        
        if len(folderPathText) > 0 and len(repoNameText) > 0 and " " not in repoNameText:
            folderPathItem = QTableWidgetItem(folderPathText)
            repoNameItem = QTableWidgetItem(repoNameText)
            
            self.FolderList.setRowCount(row + 1)
            self.FolderList.setItem(row, 0, folderPathItem)
            self.FolderList.setItem(row, 1, repoNameItem)
        
    def DeleteLine(self): 
        row = self.FolderList.currentRow()
        
        self.FolderList.removeRow(row)
        
    def UploadFolder(self):
        buttonReply = QMessageBox.information(self, "System", "Do you want to upload folders?", QMessageBox.Yes | QMessageBox.No)
        
        if buttonReply == QMessageBox.No:
            QMessageBox.information(self, "System", "Upload Canceled")
        elif buttonReply == QMessageBox.Yes:
            global id, pw
        
            pathRepoDict = {}
            repoPathDict = {}
            
            row = self.FolderList.rowCount()
            
            for r in range(0, row):
                pathName = self.FolderList.item(r, 0).text()
                repoName = self.FolderList.item(r, 1).text()
                
                try:
                    pathRepoDict[pathName]
                except:
                    try:
                        repoPathDict[repoName]
                    except:
                        repoPathDict[repoName] = pathName
                        pathRepoDict[pathName] = repoName
            
            try:
                repoURLDict = GitUploder.GetRemoteURL(repoPathDict.keys(), id, pw)
            except GitUploder.LogInFailure:
                repoURLDict = {}
                QMessageBox.information(self, "System", "LogIn failure. Please check ID/PW.")
            else:
                GitUploder.CommitFolders(repoPathDict.keys(), repoPathDict, repoURLDict)
            
                QMessageBox.information(self, "System", "Commit Complete")
    
    def SetUserInfo(self):
        global id, pw
        
        id = self.ID.text()
        self.ID.setText("")
        self.ID.setEnabled(False)
        
        pw = self.PW.text()
        self.PW.setText("")
        self.PW.setEnabled(False)

        QMessageBox.information(self, "System", "Setting Complete")
        
    def ResetUserInfo(self):
        global id, pw
        
        self.ID.setEnabled(True)
        id = ""
        
        self.PW.setEnabled(True)
        pw = ""
        
        QMessageBox.information(self, "System", "Reset Complete")
                
if __name__ == "__main__":
    WIDTH = 600
    HEIGHT = 500
    
    app = QApplication(sys.argv)
    mainwindow = MainWindow()

    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainwindow)
    widget.setFixedWidth(WIDTH)
    widget.setFixedHeight(HEIGHT)
    widget.show()
    sys.exit(app.exec_())