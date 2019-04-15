import socket
import sys
import time
import datetime
import pickle
import hashlib
import os

class Node():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host = ''
    port = 9996

    def newSocket(self):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    def sendData(self,s,data):
        s.send(sys.getsizeof(data).to_bytes(4,byteorder = 'big'))
        try:
            s.send(data.encode())
        except Exception:
            print('The connection has been lost.')
            exit(1)
    def recvData(self,s):
        size = int.from_bytes(s.recv(4),byteorder = 'big')
        data = s.recv(size).decode()
        return data

class User():
    def __init__(self,name):
        self.name = name
        self.followlist = []
        self.messagelist = []
    def addUser(self,name):
        self.followlist.append(name)
    def deleteUser(self,name):
        self.followlist.remove(name)
    def addMessage(self,message):
        self.messagelist.append(message)
    def deleteMessage(self,num):
        del self.messagelist[-num]
        print(self.messagelist)
    def isFollow(self,user):
        return user in self.followlist
    def getName(self):
        return self.name
    def getFollowList(self):
        return self.followlist
    def getMessageList(self):
        return self.messagelist

class client(Node): 
    def __init__(self):
        print(socket.gethostname())
        host = socket.gethostbyname(socket.gethostname())
        print(host)
    
    def login(self): 
        try:
            self.s.connect((self.host,self.port))
        except ConnectionRefusedError as e:
            print("You can't log in. Check your connection with the server.")
            return False
        self.sendData(self.s,'login')
        print('A Simple Text-based SNS')
        check = input('Do you have an account in this server? If you have,please enter Y.')
        self.sendData(self.s,check)
        if check == 'Y':
            while True:
                print('LOG IN')
                account = []
                account.append(input('Please enter your ID : '))
                account.append(input('Please enter your password(only use number or alphabet) : '))
                self.sendData(self.s,'/'.join(account))
                checkAcc = self.recvData(self.s)
                if checkAcc == 'Y':
                    self.name = self.recvData(self.s)
                    break  
                print('Please enter the correct ',checkAcc)
        else:
            print('Sign Up')
            while True:
                account = []
                while True:
                    ID = input('Please enter your ID : ')
                    if len(ID) <= 10:
                        account.append(ID)
                        break
                    print('ID is less than 10 characters.')
                while True:
                    password = input('Please enter your password(only use number or alphabet) : ')
                    if len(password) <= 10:
                        account.append(password)
                        break
                    print('Password is less than 10 characters.')
                while True:
                    name = input('Please enter your name : ')
                    if len(name) <= 8:
                        account.append(name)
                        break
                    print('Name is less than 8 characters.')
                self.sendData(self.s,'/'.join(account))
                checkAcc = self.recvData(self.s)
                if checkAcc == 'Y':
                    self.name = account[2]
                    break
                print('There is same ',checkAcc)
        print('\nWelcome {}!\n'.format(self.name))
        self.readTimeline()
        self.s.close()
        return True

    def execute(self):
        while(1):
            self.newSocket()
            order = input('What would you do (POST, DELETE, FOLLOW, UNFOLLOW, UPDATE, QUIT) ? ')
            try:
                self.s.connect((self.host,self.port))
            except ConnectionRefusedError as e:
                print("Check your connection with the server.")
                return
            self.sendData(self.s,'progress')
            time.sleep(0.3)
            self.sendData(self.s,order)
            time.sleep(0.3)
            self.sendData(self.s,self.name)
            if order == 'POST':
                self.post()
            elif order == 'DELETE':
                self.delete()
            elif order == 'FOLLOW':
                self.follow()
            elif order == 'UNFOLLOW':
                self.unfollow()
            elif order == 'UPDATE':
                pass
            elif order == 'QUIT':
                print('connection closed')
                return
            else:
                print('Please try again. You must not enter other word.')
            self.readTimeline()
            self.s.close()

    def readTimeline(self): 
        rawdata = self.recvData(self.s)
        data = list()
        if rawdata == 'None':
            print('timeline is empty\n')
        else:
            rawdata = rawdata.split('||')
            for i in rawdata:
                data.append(i.split('/'))   
            print('Your timeline: ')
            for i in [1,2,3]:
                if len(data) >= i:
                    print("<{}> by '{}'".format(data[-i][1],data[-i][0]))
                    print(data[-i][2])
                    print(data[-i][4])
                    print('----')
            if len(data) >= 4:
                print('(... about {} more messages)'.format(len(data)-3))
                if input() == chr(0x41):
                    for i in range(4,len(data)+1):
                        print("<{}> by '{}'".format(data[-i][1],data[-i][0]))
                        print(data[-i][2])
                        print(data[-i][4])
                        print('----')

    def post(self):
        while True:
            title = input('\nTitle: ')
            if len(title) <= 20:
                break
            print('Title is less than 20 characters.')
        while True:
            content = input('Content: ')
            if len(content) <= 150:
                break
            print('Content is less than 150 characters.')
        m =[self.name,title,content,str(time.time()),datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        self.sendData(self.s,'/'.join(m))
        print('\nA new message is successfully posted\n')

    def delete(self):
        rawdata = self.recvData(self.s).split('||')
        print(rawdata)
        if rawdata == ['None']:
            print("There is no message to delete.\n")
            return
        print('Your posted messages')
        data = list()        
        for i in rawdata:
            data.append(i.split('/'))
        for i in [1,2]:
            if len(data) >= i:
                print("#{:02d} <{}> {}".format(i,data[-i][1],data[-i][4]))
        if len(data) >= 3:
            print('...')
            if input() == chr(0x41):
                for i in range(3,len(data)+1):
                    print("#{:02d} <{}> {}".format(i,data[-i][1],data[-i][4]))

        num = input('Which one do you want to delete? ')
        self.sendData(self.s,num)
        print('\nThe message is successfully deleted!')
    
    def follow(self):
        data = self.recvData(self.s).split('/')
        if data == ['None']:
            print("There is no one to follow.")
            return
        print('You can follow these users\n')

        for i in data:
            print(i)
        who = input('\nWhom do you want to follow? ')
        while not who in data:
            print('Please try again. You must choose this list.')
            who = input('Whom do you want to follow? ')
        self.sendData(self.s,who)
        print('\nNow, you are following {}!\n'.format(who))

    def unfollow(self):
        data = self.recvData(self.s).split('/')
        if data == ['None']:
            print("There is no one to unfollow.")
            return
        print('You can unfollow these users\n')        
        for i in data:
            print(i)
        who = input('\nWhom do you want to unfollow? ')
        while not who in data:
            print('Please try again. You must choose this list.')
            who = input('Whom do you want to unfollow? ')
        self.sendData(self.s,who)
        print('From this time, your are not following {}!\n'.format(who))

class server(Node):
    def __init__(self):
        self.s.bind((self.host,self.port))
        self.s.listen(1)
        if not os.path.exists('account.bin'):
            open('account.bin','w')
        if not os.path.exists('data.bin'):
            open('data.bin','w')

    def execute(self):
        self.userlist = []
        self.umlist = []
        while(1):
            conn,addr= self.s.accept()
            mode = self.recvData(conn)
            if mode == 'login':
                accountlist = []
                with open('account.bin','rb') as f:
                    while True:
                        try:
                            a = pickle.load(f)
                            accountlist.append(a)
                        except EOFError:
                            break
                check = self.recvData(conn)
                if check == 'Y':#log in
                    while True:
                        acc = self.recvData(conn).split('/')
                        ck = False
                        for account in accountlist:
                            if acc[0] == account[0]:
                                if acc[1] == account[1]:
                                    ck = True
                                    self.sendData(conn,'Y')
                                    time.sleep(0.3)
                                    self.sendData(conn,account[2])
                                    self.name = account[2]
                                    break
                                else:
                                    self.sendData(conn,'password')
                            else:
                                self.sendData(conn,'ID')
                        if ck:
                            break
                else:##sign up
                    while True:
                        acc = self.recvData(conn).split('/')
                        ck = False
                        for account in accountlist:
                            if acc[0] == account[0]:
                                ck = True
                                self.sendData(conn,'ID')
                                break
                            if acc[2] == account[2]:
                                ck = True
                                self.sendData(conn,'name')
                                break
                        if not ck:
                            self.sendData(conn,'Y')
                            self.name = acc[2]
                            accountlist.append(acc)
                            with open('account.bin','wb') as f:
                                for acc in accountlist:
                                    pickle.dump(acc,f)
                            break
                print(self.name,'Signed in')
                self.loadData()
                self.user = User(self.name)
                for user in self.umlist:
                    if user.getName() == self.name:
                        self.user = user
                if not self.name in self.userlist:
                    self.umlist.append(self.user)
                    self.user.addUser(self.user.getName())
                    self.userlist.append(self.user.getName())
                self.sendTimeline(conn)
                self.saveData()

            else:
                print('connection waiting...')
                order = self.recvData(conn)
                user_name = self.recvData(conn)
                self.user = User(user_name)
                for user in self.umlist:
                    if user.getName() == user_name:
                        self.user = user
                print(user_name,'is connected')
                self.loadData()
                if order == 'POST':
                    self.post(conn)
                elif order == 'DELETE':
                    self.delete(conn)
                elif order == 'FOLLOW':
                    self.follow(conn)
                elif order == 'UNFOLLOW':
                    self.unfollow(conn)
                elif order == 'QUIT':
                    print('connection closed')
                self.sendTimeline(conn)
                self.saveData()
            conn.close()
    
    def loadData(self):
        with open('data.bin','rb') as f: #data.bin : list of user
            self.userlist = []
            self.umlist = []
            while True:
                try:
                    user = pickle.load(f)
                except EOFError:
                    break
                self.umlist.append(user)
                self.userlist.append(user.getName())
    
    def saveData(self):
        with open('data.bin','wb') as f:
            for user in self.umlist:
                pickle.dump(user,f)

    def sendTimeline(self,conn):
        rawtimeline = []
        for user in self.umlist:
            if user.getName() in self.user.getFollowList(): 
                rawtimeline+=user.getMessageList()
        rawtimeline.sort(key = lambda x:x[3])
        timeline = []
        for m in rawtimeline:
            m = '/'.join(m)
            timeline.append(m)
        if timeline == []:
            self.sendData(conn,'None')
        else:
            self.sendData(conn,'||'.join(timeline))

    def post(self,conn):
        message = self.recvData(conn).split('/')
        for user in self.umlist:
            if user.getName() == self.user.getName():
                user.addMessage(message)

    def delete(self,conn):
        messagelist = []
        for m in self.user.getMessageList():
            messagelist.append('/'.join(m))
        if messagelist == []:
            self.sendData(conn,'None')
            return
        else:
            self.sendData(conn,'||'.join(messagelist))
        num = int(self.recvData(conn))
        for user in self.umlist:
            if user.getName() == self.user.getName():
                user.deleteMessage(num)    
        self.user.deleteMessage(num)

    def follow(self,conn):
        CanFollowList = []
        for user in self.umlist:
            if not user.getName() in self.user.getFollowList():
                CanFollowList.append(user.getName())
        if CanFollowList == []:
            self.sendData(conn,'None')
            return
        else:
            self.sendData(conn,'/'.join(CanFollowList))
        who = self.recvData(conn)
        for user in self.umlist:
            if user.getName() == self.user.getName():
                user.addUser(who)
        self.user.addUser(who)

    def unfollow(self,conn):
        CanUnfollowList = []
        for user in self.user.getFollowList():
            if user != self.user.getName():
                CanUnfollowList.append(user)
        if CanUnfollowList == []:
            self.sendData(conn,'None')
            return
        else:
            self.sendData(conn,'/'.join(CanUnfollowList))
        who = self.recvData(conn)
        for user in self.umlist:
            if user.getName() == self.user.getName():
                user.deleteUser(who)
        self.user.deleteUser(who)
