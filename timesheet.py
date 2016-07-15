import time, sys, serial, datetime, sqlite3, re
from serialchk import usePort, serial_ports, serPort

# Find the serial port used by RFID

sqlite_file = '/Volumes/ZAI-Enrypted/notes/timesheet/timesheet.sqlite'
logtbl = 'timelogT'
code = ''
    
myPort = serPort('FT232R')
print myPort


serial = serial.Serial(myPort, baudrate=9600)

while serial.read():

    data = serial.read()
    
    if data == '\r':
        unxtme = str(time.time())
        timestmp = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        
        # Remove bad leading characters that have control structure
        codeout = re.sub(r'\W+', '', code)
        print(codeout)
        print(timestmp)

        # Connect to the database
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()
        
        # Get the last inserted ID
        c.execute("SELECT * from SQLITE_SEQUENCE WHERE `name`='"+logtbl+"';")
        lastID = c.fetchone()
        lastIDs = str(lastID[1])

        # In = 1; Out = 0
        # Select the last row of data
        c.execute("SELECT RFID, inout FROM "+logtbl+" WHERE ID = "+lastIDs)
        lastData = c.fetchone()
        print lastData[1]
        if (lastData[1] == 0):
            newInOut = "1"
        else:
            # Check to see if the RFID card changed.
            if (lastData[0] != codeout):
                c.execute("INSERT INTO `main`.`"+logtbl+"` (`RFID`, `tstamp`, `inout`) VALUES ('"+lastData[0]+"','"+unxtme+"',0)")
                newInOut = "1"
            else:
                newInOut = "0"
        
        c.execute("INSERT INTO `main`.`"+logtbl+"` (`RFID`, `tstamp`, `inout`) VALUES ('"+codeout+"','"+unxtme+"',"+newInOut+")")
        conn.commit()
        conn.close()
        code =''
        
    else:
        code += data
    
serial.close()

