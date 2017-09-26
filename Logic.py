import socket
import sqlite3
import pickle
import struct
import pandas as pd


class LogicLayer:
    """
    Class containing logic for interacting with the database.
    
    INPUT:
      dbName - Path to database (string)
    """

    
    def __init__(self, dbName='students.db'):
        """
        Create a connection object and cursor for the specified database file 
        (default students.db)
        """
        
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()
        self.colNames = '(first_name, last_name)'

        
    def ConnectUI(self, TCP_IP='127.0.0.1', TCP_PORT=5005):
        """
        Create socket and wait for connection from UI.
    
        INPUT:
          TCP_IP   - IP address
          TCP_PORT - Port
        """

        clientInitMsg = b'Hello Logic'
        serverInitReply = b'Hello UI'
        buffSize = 4

        # Create socket
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSock.bind((TCP_IP, TCP_PORT))
        self.serverSock.listen(1)
        self.clientSock, addr = self.serverSock.accept()

        # Look for the initial hello message
        data = self.clientSock.recv(len(clientInitMsg))

        # If the hello message was received, send the response
        if data == clientInitMsg:
            try:
                self.clientSock.sendall(serverInitReply)
            except:
                print('Error sending data')

    def WaitForMessages(self):
        buffSize = 4
        
        # Continue looking for messages from client
        connectionOpen = True
        while connectionOpen:
            buff = self.clientSock.recv(buffSize)
            if buff is not None:
                msgSize = struct.unpack('<i', buff)[0]
                buff = self.clientSock.recv(msgSize)
                connectionOpen = self.ProcessMessage(buff)
                

    def ProcessMessage(self, msg_orig):
        """
        Process instructions from UI.

        INPUT:
          msg_orig - Pickled dictionary containing command information
        """

        msg = pickle.loads(msg_orig)
        
        if msg['cmd'] == 'GetStudents':
            reply = pickle.dumps(self.GetStudents())
            self.clientSock.sendall(reply)
            return True

        elif msg['cmd'] == 'AddStudent':
            self.AddStudent(msg['data']['values'])
            return True
        
        elif msg['cmd'] == 'DeleteStudent':
            self.RemoveStudent(msg['data']['ID'])
            return True

        elif msg['cmd'] == 'UpdateStudent':
            self.UpdateStudent(msg['data']['ID'], msg['data']['values'])
            return True

        elif msg['cmd'] == 'CloseSocket':
            self.clientSock.close()
            return False
            

    def AddStudent(self, values=None):
        """
        Add a student with the given name to the database.
        
        INPUT:
          values - Dictionary with key/pair of column name/student info 
        """

        if values is not None:
            formattedValues = (None, values['first_name'], values['last_name'])
            valStr = ','.join(['?'] * len(formattedValues))
            sqlStatement = 'INSERT INTO students VALUES (%s)' % valStr
            self.cursor.execute(sqlStatement, formattedValues)
            self.conn.commit()

            
    def UpdateStudent(self, id=None, values=None):
        """
        Update student with the given ID in the database.

        INPUT:
          id     - Student's ID number in database
          values - Dictionary with key/pair of column name/student info 
        """

        if id is not None and values is not None:
            formattedValues =  (values['first_name'], values['last_name'], id)
            self.cursor.execute('''UPDATE students SET first_name = ?, 
                                   last_name = ? WHERE id = ?''',
                                formattedValues)
            self.conn.commit()

            
    def RemoveStudent(self, id=None):
        """
        Remove student with the given ID from the database.

        INPUT:
          id     - Student's ID number in database
        """

        if id is not None:
            secureID = (id,)
            self.cursor.execute('DELETE FROM students WHERE id = ?',  secureID)
            self.conn.commit()

            
    def GetStudents(self):
        """
        Return all students in the database.

        OUTPUT:
          df - DataFrame with columns for ID, First Name, and Last Name
        """
        df = pd.read_sql_query('''SELECT id AS ID, first_name AS "First Name", 
                                  last_name AS "Last Name" FROM students''',
                               self.conn)
        return df

    
if __name__ == '__main__':
    
    ll = LogicLayer()
    ll.ConnectUI()
    ll.WaitForMessages()
