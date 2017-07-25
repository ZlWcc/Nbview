import pymysql, os, re, time
from threading import Thread, Lock
from tkinter import *
from tkinter import ttk


config={
    'host':'localhost',
    'user':'root',
    'password':'123456',
    'db':'ServersList',
    'charset':'utf8mb4',
    'cursorclass':pymysql.cursors.DictCursor,
    }
conn=pymysql.connect(**config)
mutex = Lock()#创建锁
thread_count = 0


#================获取地址信息=====================
def getData():
    try:
        with conn.cursor() as cursor:
            sql='select * from servers'
            cursor.execute(sql)
            rs = cursor.fetchall()
            return rs
    except Exception as e:
        print ("getData出现问题： " + str(e))



#==========将ping的结果返回到数据库中==============
def ist_rs(id,rs):
    try:
        with conn.cursor() as cursor:
            rs=rs[0]
            sql = 'SELECT * FROM ping WHERE id=%s' %id
            cursor.execute(sql)
            result = cursor.fetchall()
            if len(result) == 0:
                sql = 'INSERT INTO ping (id, minping, maxping, aveping) VALUES(%s, %s, %s, %s)' %(id,rs[0],rs[1],rs[2])
            else:
                sql= 'UPDATE ping SET minping=%s, maxping=%s, aveping=%s WHERE id=%s' %(rs[0],rs[1],rs[2],id)
#             print(sql)
            cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print ("its_rs出现问题： " + str(e),id)



#============若超时，记录 timeout+1 ========================
def add_timeout(id):
    try:
        with conn.cursor() as cursor:
            sql = 'SELECT timeout FROM ping WHERE id=%s' %id
            cursor.execute(sql)
            result = cursor.fetchall()
            if len(result) == 0:
                sql = 'INSERT INTO ping (id, timeout) VALUES(%s, 1)' %id
            else:
                times = int(result[0]['timeout']) + 1
                sql = 'UPDATE ping SET timeout=%s WHERE id=%s' %(times, id)
#             print(sql)
            cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print ("add_timeout出现问题： " + str(e),id)

#=================对地址进行多线程ping============
def ping_thread(id,ip):
    global thread_count
    ping = 'ping this'.replace('this',ip)
    line = os.popen(ping).read()
    ping_time = re.findall(r"最短 = (\d+)ms，最长 = (\d+)ms，平均 = (\d+)ms", line)
    mutex.acquire()#取得锁
    if len(ping_time) == 1:
        ist_rs(id,ping_time)
    else:
        add_timeout(id)
    thread_count = thread_count - 1
    mutex.release()#释放锁




def update_ping():
    global thread_count
    urllist = getData()
    if len(urllist) > 0:
        for r in urllist:
            id, ip = r['id'], r['PPTP']
            Thread(target=ping_thread, args=(id,ip)).start()
            thread_count += 1
        while thread_count > 0:
            time.sleep(5)
            tell = 'Threading Ping ....rest(%d)' %thread_count
            print(tell)
            text_Input.set(tell)
    else:
        print('出现问题，请检查server数据库')


#  查询网络状况良好的ip
def select_servers():
    with conn.cursor() as cursor:
        sql="""select regionname,country,city,aveping,PPTP from servers s,ping p
            where s.id=p.id and
            p.timeout=0
            order by p.aveping ASC
            """
        cursor.execute(sql)
        rs = cursor.fetchall()
        return rs[:10]


#=======================GUI============================



#    top====================
root = Tk()
root.geometry("700x500+70+0")
root.title("Auto Ping Panel")
text_Input = StringVar()
Tops = Frame(root, width=600, height=90, bg="powder blue", relief=SUNKEN)
Tops.pack(side=TOP)

f1 = Frame(root, width=200, height=400, bg="powder blue", relief=SUNKEN)
f1.pack(side=LEFT)

f2 = Frame(root, width=500, height=400, bg="powder blue", relief=SUNKEN)
f2.pack(side=RIGHT)

#    func==========
def showTop10():
    tree.delete(*tree.get_children(''))
    a = select_servers()
    for i in a:
        tree.insert('','end', values=(i['regionname'],i['country'],i['city'],i['aveping'],i['PPTP']))


def update():
    update_ping()
    showTop10()


#  f1 按钮区===================
lb1Info = Label(Tops, font=('arial', 30, 'bold'), text='Auto Ping', fg='Steel Blue', bd=10, anchor='w' )
lb1Info.grid(row=0, column=0)

btnUpdate = Button(f1, bd=8, fg="black", font=('arial', 10, 'bold' ), text='Update', bg='#D3D3D3',width=10,
              command=update).grid(row=0, column=0)
btnTop10 = Button(f1, pady=3, bd=8, fg="black", font=('arial', 10, 'bold' ), text='Show10', bg='#D3D3D3', width=10,
              command=showTop10).grid(row=1, column=0)
close = Button(f1, pady=3, bd=8, fg="black", font=('arial', 10, 'bold' ), text='QUIT', bg='#D3D3D3',width=10,
              command=root.destroy).grid(row=2, column=0)

#  f2 显示区===============
#滚动条
scrollBar = Scrollbar(f2)
scrollBar.grid(row=0, column=1, rowspan=6, sticky=W+E+N+S)

#Treeview组件，5列，显示表头，带垂直滚动条
tree = ttk.Treeview(f2, columns=('c1', 'c2', 'c3', 'c4', 'c5'), show="headings", height=18, yscrollcommand=scrollBar.set)
tree.grid(row=0, column=0,sticky=W)

#设置每列宽度和对齐方式
tree.column('c1', width=80, anchor='center')
tree.column('c2', width=80, anchor='center')
tree.column('c3', width=80, anchor='center')
tree.column('c4', width=80, anchor='center')
tree.column('c5', width=180, anchor='center')

#设置每列表头标题文本
tree.heading('c1', text='RegionName')
tree.heading('c2', text='Country')
tree.heading('c3', text='City')
tree.heading('c4', text='AvePing')
tree.heading('c5', text='PPTP')

#Treeview组件与垂直滚动条结合
scrollBar.config(command=tree.yview)

#文本框
e1 = Entry(f2, textvariable=text_Input)
e1.grid(row=1, column=0, rowspan=1,sticky=W+E)

#定义并绑定Treeview组件的鼠标单击事件
def treeviewClick(event):
    item = tree.focus()
    if not item:
        return
    value = tree.item(item)['values'][-1]
    text_Input.set(value)

tree.bind('<ButtonRelease-1>', treeviewClick)


root.mainloop()
