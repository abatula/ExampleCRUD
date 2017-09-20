import sqlite3

conn = sqlite3.connect('students.db')
c = conn.cursor()
c.execute('''CREATE TABLE students (id INTEGER PRIMARY KEY, 
                                    first_name, last_name)''')

c.execute("INSERT INTO students VALUES (null, 'Alyssa', 'Batula')")
c.execute("INSERT INTO students VALUES (null, 'Kaylee', 'Frye')")
c.execute("INSERT INTO students VALUES (null, 'Harry', 'Potter')")
c.execute("INSERT INTO students VALUES (null, 'Jon', 'Snow')")
c.execute("INSERT INTO students VALUES (null, 'Clara', 'Oswald')")
c.execute("INSERT INTO students VALUES (null, 'Anthony', 'Stark')")

conn.commit()
