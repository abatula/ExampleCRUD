import sys
import socket
import pickle
import struct
import atexit
import pandas as pd

from PyQt5 import QtWidgets, QtCore, QtGui


class MainUI(QtWidgets.QMainWindow):
    """
    GUI for interacting with database logic.
    """

    
    def __init__(self, TCP_IP='127.0.0.1', TCP_PORT=5005):
        """
        Initialize the class and run the setup functions.

        INPUT:
          TCP_IP   - IP address
          TCP_PORT - Port
        """
        super().__init__()

        self.studentDF = None

        atexit.register(self.CleanupFunction)
        
        self.InitUI()
        self.ConnectServer(TCP_IP, TCP_PORT)
        self.UpdateStudentList()

        
    def InitUI(self):
        """
        Create the main window.
        """

        self.mainWindow = QtWidgets.QWidget()
        self.setWindowTitle('Student Database')

        self.resize(500,700)
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.textFont = QtGui.QFont()
        self.textFont.setPointSize(14)
        self.buttonFont = QtGui.QFont()
        self.buttonFont.setPointSize(18)
        self.titleFont = QtGui.QFont()
        self.titleFont.setPointSize(30)
        self.labelFont = QtGui.QFont()
        self.labelFont.setPointSize(20)

        self.studentList = QtWidgets.QListWidget(self)
        self.studentList.setFont(self.textFont)

        self.titleLabel = QtWidgets.QLabel('Students')
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setFont(self.titleFont)

        # Buttons
        self.addButton = QtWidgets.QPushButton('Add')
        self.addButton.setFont(self.buttonFont)
        self.updateButton = QtWidgets.QPushButton('Update')
        self.updateButton.setFont(self.buttonFont)
        self.deleteButton = QtWidgets.QPushButton('Delete')
        self.deleteButton.setFont(self.buttonFont)

        # Connections
        self.addButton.clicked.connect(self.CreateAddWindow)
        self.updateButton.clicked.connect(self.CreateUpdateWindow)
        self.deleteButton.clicked.connect(self.CreateDeleteWindow)
        self.studentList.itemClicked.connect(self.studentList.setCurrentItem)

        # Layout
        buttonbox = QtWidgets.QHBoxLayout()
        buttonbox.addStretch(0)
        buttonbox.addWidget(self.addButton)
        buttonbox.addWidget(self.updateButton)
        buttonbox.addWidget(self.deleteButton)
        buttonbox.addStretch(0)
        
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.titleLabel)
        vbox.addWidget(self.studentList)
        vbox.addLayout(buttonbox)

        self.mainWindow.setLayout(vbox)

        self.setCentralWidget(self.mainWindow)
        self.show()

        
    def ConnectServer(self, TCP_IP='127.0.0.1', TCP_PORT=5005):
        """
        Connect to the server run by the database logic layer.

        INPUT:
          TCP_IP   - IP address
          TCP_PORT - Port
        """
        
        clientInitMsg = b'Hello Logic'
        serverInitReply = b'Hello UI'

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((TCP_IP, TCP_PORT))
        except ConnectionRefusedError:
            self.socketConnected = False
            print('ERROR: Socket connection refused')
        else:
            # Send initial welcome
            self.sock.sendall(clientInitMsg)

            # Receive welcome message 
            try:
                buff = self.sock.recv(len(serverInitReply))
            except (socket.timeout, ConnectionResetError):
                self.sock.close()
                print('Socket Closed')

            if buff == serverInitReply:
                self.socketConnected = True

                
    def UpdateStudentList(self):
        """
        Get all students from the database and display them in the GUI.
        """
        buffSize = 1024
        
        # Get list of students
        msgdict = {'cmd':'GetStudents'}
        sendmsg = pickle.dumps(msgdict)
        sizemsg = struct.pack('<i',len(sendmsg))
        self.sock.sendall(sizemsg)
        self.sock.sendall(sendmsg)

        # Get data from the server
        buff = self.sock.recv(buffSize)
        msg = buff

        # Keep reading until message complete
        while len(buff) == buffSize:
            buff = self.sock.recv(buffSize)
            msg += buff

        # Format for display
        self.studentDF = pickle.loads(msg)
        dflist = self.studentDF.loc[:,['First Name',
                                       'Last Name']].values.tolist()
        students = [' '.join(x) for x in dflist]

        # Display student list and select first student
        self.studentList.clear()
        self.studentList.addItems(students)
        self.studentList.setCurrentRow(0)

        
    def CreateAddWindow(self):
        """
        Create a pop-up window for adding a new student.
        """
        
        self.miniWindow = QtWidgets.QWidget()
        self.miniWindow.setWindowTitle('Add Student')
        self.miniWindow.resize(500,250)
        self.PositionWindow(self.miniWindow)

        # Labels
        firstNameLabel = QtWidgets.QLabel('First Name')
        firstNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        firstNameLabel.setFont(self.labelFont)
        lastNameLabel = QtWidgets.QLabel('Last Name')
        lastNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        lastNameLabel.setFont(self.labelFont)

        # Text Lines
        self.firstNameText = QtWidgets.QLineEdit()
        self.firstNameText.setFont(self.textFont)
        self.lastNameText = QtWidgets.QLineEdit()
        self.lastNameText.setFont(self.textFont)

        # Buttons
        addStudentButton = QtWidgets.QPushButton('Add')
        addStudentButton.setFont(self.buttonFont)
        cancelButton = QtWidgets.QPushButton('Cancel')
        cancelButton.setFont(self.buttonFont)

        # Connections
        addStudentButton.clicked.connect(self.AddStudent)
        cancelButton.clicked.connect(self.miniWindow.close)

        # Layout
        buttonbox = QtWidgets.QHBoxLayout()
        buttonbox.addStretch(1)
        buttonbox.addWidget(addStudentButton)
        buttonbox.addWidget(cancelButton)
        buttonbox.addStretch(1)

        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addStretch(0)
        vbox1.addWidget(firstNameLabel)
        vbox1.addWidget(self.firstNameText)
        vbox1.addStretch(0)

        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addStretch(0)
        vbox2.addWidget(lastNameLabel)
        vbox2.addWidget(self.lastNameText)
        vbox2.addStretch(0)

        namebox = QtWidgets.QHBoxLayout()
        namebox.addStretch(0)
        namebox.addLayout(vbox1)
        namebox.addLayout(vbox2)
        namebox.addStretch(0)

        mainVbox =  QtWidgets.QVBoxLayout()
        mainVbox.addStretch(0)
        mainVbox.addLayout(namebox)
        mainVbox.addLayout(buttonbox)
        mainVbox.addStretch(0)

        self.miniWindow.setLayout(mainVbox)
        self.miniWindow.show()

        
    def CreateUpdateWindow(self):
        """
        Create a pop-up window for updating an existing student.
        """
        
        self.miniWindow = QtWidgets.QWidget()
        self.miniWindow.setWindowTitle('Update Student')
        self.miniWindow.resize(500,250)
        self.PositionWindow(self.miniWindow)

        # Get Selected student name and ID from DataFrame
        selectedRow = self.studentList.currentRow()
        self.selectedID = int(self.studentDF.loc[selectedRow, 'ID'])
        firstName = self.studentDF.loc[selectedRow, 'First Name']
        lastName = self.studentDF.loc[selectedRow, 'Last Name']
        
        # Labels
        firstNameLabel = QtWidgets.QLabel('First Name')
        firstNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        firstNameLabel.setFont(self.labelFont)
        lastNameLabel = QtWidgets.QLabel('Last Name')
        lastNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        lastNameLabel.setFont(self.labelFont)

        # Text Lines
        self.firstNameText = QtWidgets.QLineEdit()
        self.firstNameText.setFont(self.textFont)
        self.firstNameText.setText(firstName)
        self.lastNameText = QtWidgets.QLineEdit()
        self.lastNameText.setFont(self.textFont)
        self.lastNameText.setText(lastName)

        # Buttons
        updateStudentButton = QtWidgets.QPushButton('Update')
        updateStudentButton.setFont(self.buttonFont)
        cancelButton = QtWidgets.QPushButton('Cancel')
        cancelButton.setFont(self.buttonFont)

        # Connections
        updateStudentButton.clicked.connect(self.UpdateStudent)
        cancelButton.clicked.connect(self.miniWindow.close)

        # Layout
        buttonbox = QtWidgets.QHBoxLayout()
        buttonbox.addStretch(1)
        buttonbox.addWidget(updateStudentButton)
        buttonbox.addWidget(cancelButton)
        buttonbox.addStretch(1)

        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addStretch(0)
        vbox1.addWidget(firstNameLabel)
        vbox1.addWidget(self.firstNameText)
        vbox1.addStretch(0)

        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addStretch(0)
        vbox2.addWidget(lastNameLabel)
        vbox2.addWidget(self.lastNameText)
        vbox2.addStretch(0)

        namebox = QtWidgets.QHBoxLayout()
        namebox.addStretch(0)
        namebox.addLayout(vbox1)
        namebox.addLayout(vbox2)
        namebox.addStretch(0)

        mainVbox =  QtWidgets.QVBoxLayout()
        mainVbox.addStretch(0)
        mainVbox.addLayout(namebox)
        mainVbox.addLayout(buttonbox)
        mainVbox.addStretch(0)

        self.miniWindow.setLayout(mainVbox)
        self.miniWindow.show()


    def CreateDeleteWindow(self):
        """
        Create a pop-up window confirming student deletion.
        """
        
        self.miniWindow = QtWidgets.QWidget()
        self.miniWindow.setWindowTitle('Delete Student')
        self.miniWindow.resize(500,250)
        self.PositionWindow(self.miniWindow)

        # Get Selected student name and ID from DataFrame
        selectedRow = self.studentList.currentRow()
        self.selectedID = int(self.studentDF.loc[selectedRow, 'ID'])
        studentName = ' '.join([self.studentDF.loc[selectedRow, 'First Name'],
                                self.studentDF.loc[selectedRow, 'Last Name']])

        # Labels
        textLabel = QtWidgets.QLabel('Delete %s from database?' % studentName)
        textLabel.setAlignment(QtCore.Qt.AlignCenter)
        textLabel.setFont(self.labelFont)

        # Buttons
        confirmButton = QtWidgets.QPushButton('Confirm')
        confirmButton.setFont(self.buttonFont)
        cancelButton = QtWidgets.QPushButton('Cancel')
        cancelButton.setFont(self.buttonFont)

        # Connections
        confirmButton.clicked.connect(self.DeleteStudent)
        cancelButton.clicked.connect(self.miniWindow.close)

        # Layout
        buttonbox = QtWidgets.QHBoxLayout()
        buttonbox.addStretch(1)
        buttonbox.addWidget(confirmButton)
        buttonbox.addWidget(cancelButton)
        buttonbox.addStretch(1)

        vbox =  QtWidgets.QVBoxLayout()
        vbox.addStretch(0)
        vbox.addWidget(textLabel)
        vbox.addStretch(0)
        vbox.addLayout(buttonbox)
        vbox.addStretch(0)

        self.miniWindow.setLayout(vbox)
        self.miniWindow.show()

        
    def AddStudent(self):
        """
        Send message to server to add student to the database.

        Message sent as a little-endian message indicating buffer size followed 
        by a pickled dictionary containing instructions and student information.
        """
        
        firstName = self.firstNameText.text()
        lastName = self.lastNameText.text()
        msgdict = {'cmd':'AddStudent',
                   'data':{'values':{'first_name':firstName,
                                     'last_name':lastName}}}
        sendmsg = pickle.dumps(msgdict)
        sizemsg = struct.pack('<i',len(sendmsg))
        self.sock.sendall(sizemsg)
        self.sock.sendall(sendmsg)

        self.UpdateStudentList()
        self.miniWindow.close()


    def DeleteStudent(self):
        """
        Send message to server to delete a student from the database.

        Message sent as a little-endian message indicating buffer size followed 
        by a pickled dictionary containing instructions and student information.
        """
        
        msgdict = {'cmd':'DeleteStudent',
                   'data':{'ID':self.selectedID}}
        sendmsg = pickle.dumps(msgdict)
        sizemsg = struct.pack('<i',len(sendmsg))
        self.sock.sendall(sizemsg)
        self.sock.sendall(sendmsg)

        self.UpdateStudentList()
        self.miniWindow.close()

        
    def UpdateStudent(self):
        """
        Send message to server to update a student in the database.

        Message sent as a little-endian message indicating buffer size followed 
        by a pickled dictionary containing instructions and student information.
        """
        
        firstName = self.firstNameText.text()
        lastName = self.lastNameText.text()
        msgdict = {'cmd':'UpdateStudent',
                   'data':{'ID':self.selectedID,
                           'values':{'first_name':firstName,
                                     'last_name':lastName}}}
        sendmsg = pickle.dumps(msgdict)
        sizemsg = struct.pack('<i',len(sendmsg))
        self.sock.sendall(sizemsg)
        self.sock.sendall(sendmsg)

        self.UpdateStudentList()
        self.miniWindow.close()

        
    def PositionWindow(self, window):
        """
        Center display window on the screen.

        INPUT:
            window  - The window to be moved
        """
        
        # Center the window
        qtRectangle = window.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        window.move(qtRectangle.topLeft())


    def CleanupFunction(self):
        """
        Send message to server to close connection when program exits.

        Message sent as a little-endian message indicating buffer size followed 
        by a pickled dictionary containing instructions and student information.
        """
        msgdict = {'cmd':'CloseSocket'}
        sendmsg = pickle.dumps(msgdict)
        sizemsg = struct.pack('<i',len(sendmsg))
        self.sock.sendall(sizemsg)
        self.sock.sendall(sendmsg)
        

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    ex = MainUI()
    sys.exit(app.exec_())
