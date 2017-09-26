import unittest
import os
import sqlite3
import socket
import pickle
import struct
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

        self.assertTrue(df.equals(expectedDF), 'Did not remove student properly')

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

        self.assertTrue(df.equals(expectedDF), 'Did not update student properly')



if __name__ == '__main__':
    unittest.main()
