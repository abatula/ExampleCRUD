import unittest
from unittest.mock import patch

import os
import sqlite3
import pickle
import socket
import pandas as pd

import Logic

class TestLogicDB(unittest.TestCase):

    def setUp(self):
        self.dbname = 'test.db'
        self.conn = sqlite3.connect(self.dbname)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE students (id INTEGER PRIMARY KEY, 
                          first_name, last_name)''')

        self.c.execute("INSERT INTO students VALUES (null, 'Alyssa', 'Batula')")
        self.c.execute("INSERT INTO students VALUES (null, 'Kaylee', 'Frye')")
        self.c.execute("INSERT INTO students VALUES (null, 'Harry', 'Potter')")
        self.c.execute("INSERT INTO students VALUES (null, 'Jon', 'Snow')")
        self.c.execute("INSERT INTO students VALUES (null, 'Clara', 'Oswald')")
        self.c.execute("INSERT INTO students VALUES (null, 'Anthony', 'Stark')")

        self.conn.commit()        

        self.Logic = Logic.LogicLayer(self.dbname)

        
    def tearDown(self):
        self.conn.close()
        os.remove(self.dbname)

        
    def test_GetStudents(self):

        df = self.Logic.GetStudents()

        dfContents = [[1, 'Alyssa', 'Batula'],
                      [2, 'Kaylee', 'Frye'],
                      [3, 'Harry', 'Potter'],
                      [4, 'Jon', 'Snow'],
                      [5, 'Clara', 'Oswald'],
                      [6, 'Anthony', 'Stark']]
        columns = ['ID', 'First Name', 'Last Name']
        expectedDF = pd.DataFrame(data=dfContents, index=None, columns=columns)
        
        self.assertTrue(df.equals(expectedDF), 'Returned incorrect DataFrame')

        
    def test_AddStudent(self):

        values = {'first_name':'Luke', 'last_name':'Skywalker'}
        self.Logic.AddStudent(values)
        df = self.Logic.GetStudents()

        dfContents = [[1, 'Alyssa', 'Batula'],
                      [2, 'Kaylee', 'Frye'],
                      [3, 'Harry', 'Potter'],
                      [4, 'Jon', 'Snow'],
                      [5, 'Clara', 'Oswald'],
                      [6, 'Anthony', 'Stark'],
                      [7, 'Luke', 'Skywalker']]
        columns = ['ID', 'First Name', 'Last Name']
        expectedDF = pd.DataFrame(data=dfContents, index=None, columns=columns)

        self.assertTrue(df.equals(expectedDF), 'Did not add student properly')

        
    def test_RemoveStudent(self):

        removeID = 3
        self.Logic.RemoveStudent(removeID)
        df = self.Logic.GetStudents()

        dfContents = [[1, 'Alyssa', 'Batula'],
                      [2, 'Kaylee', 'Frye'],
                      [4, 'Jon', 'Snow'],
                      [5, 'Clara', 'Oswald'],
                      [6, 'Anthony', 'Stark']]
        columns = ['ID', 'First Name', 'Last Name']
        expectedDF = pd.DataFrame(data=dfContents, index=None, columns=columns)

        self.assertTrue(df.equals(expectedDF),
                        'Did not remove student properly')

        
    def test_UpdateStudent(self):

        updateID = 5
        values = {'first_name':'Oswin', 'last_name':'Oswald'}
        self.Logic.UpdateStudent(updateID, values)
        df = self.Logic.GetStudents()

        dfContents = [[1, 'Alyssa', 'Batula'],
                      [2, 'Kaylee', 'Frye'],
                      [3, 'Harry', 'Potter'],
                      [4, 'Jon', 'Snow'],
                      [5, 'Oswin', 'Oswald'],
                      [6, 'Anthony', 'Stark']]
        columns = ['ID', 'First Name', 'Last Name']
        expectedDF = pd.DataFrame(data=dfContents, index=None, columns=columns)

        self.assertTrue(df.equals(expectedDF),
                        'Did not update student properly')

        
class TestLogicConnection(unittest.TestCase):
    
    def setUp(self):
        
        self.dbname = 'test.db'
        self.conn = sqlite3.connect(self.dbname)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE students (id INTEGER PRIMARY KEY, 
                          first_name, last_name)''')

        self.c.execute("INSERT INTO students VALUES (null, 'Alyssa', 'Batula')")
        self.c.execute("INSERT INTO students VALUES (null, 'Kaylee', 'Frye')")
        self.c.execute("INSERT INTO students VALUES (null, 'Harry', 'Potter')")
        self.c.execute("INSERT INTO students VALUES (null, 'Jon', 'Snow')")
        self.c.execute("INSERT INTO students VALUES (null, 'Clara', 'Oswald')")
        self.c.execute("INSERT INTO students VALUES (null, 'Anthony', 'Stark')")

        self.conn.commit()

        
    def tearDown(self):
        
        self.conn.close()
        os.remove(self.dbname)

        
    def test_ConnectUI(self):
        
        TCP_IP = '127.0.0.1'
        TCP_PORT=5005
        clientInitMsg = b'Hello Logic'
        serverInitReply = b'Hello UI'
    
        with patch('Logic.socket.socket') as mock_socket:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mock_socket.return_value.accept.return_value = (sock, TCP_IP)
            mock_socket.return_value.recv.return_value = clientInitMsg
            self.Logic = Logic.LogicLayer(self.dbname)
            self.Logic.ConnectUI(TCP_IP=TCP_IP, TCP_PORT=TCP_PORT)

            self.Logic.serverSock.listen.assert_called_once()
            self.Logic.serverSock.sendall.assert_called_once_with(serverInitReply)
            

    def test_ProcessMessage_Get(self):

        dfContents = [[1, 'Alyssa', 'Batula'],
                      [2, 'Kaylee', 'Frye'],
                      [3, 'Harry', 'Potter'],
                      [4, 'Jon', 'Snow'],
                      [5, 'Clara', 'Oswald'],
                      [6, 'Anthony', 'Stark']]
        columns = ['ID', 'First Name', 'Last Name']
        expectedDF = pd.DataFrame(data=dfContents, index=None, columns=columns)
        expectedReply = pickle.dumps(expectedDF)

        msgdict = {'cmd':'GetStudents'}
        sendmsg = pickle.dumps(msgdict)

        TCP_IP = '127.0.0.1'
        TCP_PORT=5005

        with patch('Logic.socket.socket') as mock_socket:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mock_socket.return_value.accept.return_value = (sock, TCP_IP)
            self.Logic = Logic.LogicLayer(self.dbname)
            self.Logic.ConnectUI(TCP_IP=TCP_IP, TCP_PORT=TCP_PORT)
            self.Logic.ProcessMessage(sendmsg)
            
            self.Logic.clientSock.sendall.assert_called_once_with(expectedReply)
            

    def test_ProcessMessage_Add(self):

        dfContents = [[1, 'Alyssa', 'Batula'],
                      [2, 'Kaylee', 'Frye'],
                      [3, 'Harry', 'Potter'],
                      [4, 'Jon', 'Snow'],
                      [5, 'Clara', 'Oswald'],
                      [6, 'Anthony', 'Stark'],
                      [7, 'Luke', 'Skywalker']]
        columns = ['ID', 'First Name', 'Last Name']
        expectedDF = pd.DataFrame(data=dfContents, index=None, columns=columns)

        msgdict = {'cmd':'AddStudent',
                   'data':{'values':{'first_name':'Luke',
                                     'last_name':'Skywalker'}}}
        sendmsg = pickle.dumps(msgdict)

        TCP_IP = '127.0.0.1'
        TCP_PORT=5005

        with patch('Logic.socket.socket') as mock_socket:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mock_socket.return_value.accept.return_value = (sock, TCP_IP)
            self.Logic = Logic.LogicLayer(self.dbname)
            self.Logic.ConnectUI(TCP_IP=TCP_IP, TCP_PORT=TCP_PORT)
            self.Logic.ProcessMessage(sendmsg)

            df = pd.read_sql_query('''SELECT id AS ID, 
                                      first_name AS "First Name", 
                                      last_name AS "Last Name" FROM students''',
                               self.Logic.conn)
            
            self.assertTrue(df.equals(expectedDF),
                            'Did not add student properly')
            

    def test_ProcessMessage_Update(self):

        dfContents = [[1, 'Alyssa', 'Batula'],
                      [2, 'Kaylee', 'Frye'],
                      [3, 'Harry', 'Potter'],
                      [4, 'Jon', 'Snow'],
                      [5, 'Clara', 'Oswald'],
                      [6, 'Tony', 'Stark']]
        columns = ['ID', 'First Name', 'Last Name']
        expectedDF = pd.DataFrame(data=dfContents, index=None, columns=columns)

        msgdict = {'cmd':'UpdateStudent',
                   'data':{'ID':6,
                           'values':{'first_name':'Tony',
                                     'last_name':'Stark'}}}
        sendmsg = pickle.dumps(msgdict)

        TCP_IP = '127.0.0.1'
        TCP_PORT=5005

        with patch('Logic.socket.socket') as mock_socket:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mock_socket.return_value.accept.return_value = (sock, TCP_IP)
            self.Logic = Logic.LogicLayer(self.dbname)
            self.Logic.ConnectUI(TCP_IP=TCP_IP, TCP_PORT=TCP_PORT)
            self.Logic.ProcessMessage(sendmsg)

            df = pd.read_sql_query('''SELECT id AS ID, 
                                      first_name AS "First Name", 
                                      last_name AS "Last Name" FROM students''',
                               self.Logic.conn)
            
            self.assertTrue(df.equals(expectedDF),
                            'Did not add student properly')
            

    def test_ProcessMessage_Remove(self):

        dfContents = [[1, 'Alyssa', 'Batula'],
                      [2, 'Kaylee', 'Frye'],
                      [4, 'Jon', 'Snow'],
                      [5, 'Clara', 'Oswald'],
                      [6, 'Anthony', 'Stark']]
        columns = ['ID', 'First Name', 'Last Name']
        expectedDF = pd.DataFrame(data=dfContents, index=None, columns=columns)

        msgdict = {'cmd':'DeleteStudent',
                   'data':{'ID':3}}
        sendmsg = pickle.dumps(msgdict)

        TCP_IP = '127.0.0.1'
        TCP_PORT=5005

        with patch('Logic.socket.socket') as mock_socket:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mock_socket.return_value.accept.return_value = (sock, TCP_IP)
            self.Logic = Logic.LogicLayer(self.dbname)
            self.Logic.ConnectUI(TCP_IP=TCP_IP, TCP_PORT=TCP_PORT)
            self.Logic.ProcessMessage(sendmsg)

            df = pd.read_sql_query('''SELECT id AS ID, 
                                      first_name AS "First Name", 
                                      last_name AS "Last Name" FROM students''',
                               self.Logic.conn)
            
            self.assertTrue(df.equals(expectedDF),
                            'Did not remove student properly')


if __name__ == '__main__':
    unittest.main()
