import requests
from bs4 import BeautifulSoup as bs
import pymysql.cursors

config={
    'host':'localhost',
    'user':'root',
    'password':'123456',
    'db':'ServersList',
    'charset':'utf8mb4',
    'cursorclass':pymysql.cursors.DictCursor,
    }
conn=pymysql.connect(**config)

#=================爬取数据==================
def spider()
    url = 'https://support.purevpn.com/vpn-servers'
    html_doc = requests.get(url).content
    soup = bs(html_doc, 'html.parser')
    table = soup.find('tbody')
    return table('tr')

#================写入SQL====================

def Insert2servers(data):
    try:
        with conn.cursor() as cursor:
            sql='SELECT * FROM servers WHERE PPTP="%s"'%data[3]
            cursor.execute(sql)
            rs=cursor.fetchall()
            if len(rs) == 0:
                sql='INSERT INTO servers (RegionName,Country,City,PPTP,UDP,TCP) VALUES("%s","%s","%s","%s","%s","%s")'%tuple(data)
                cursor.execute(sql)
#                 print('succeed ',data[0])
#             else:
#                 print('has data ,skip')
        conn.commit()
    except Exception as e:
        print ("出现问题： " + str(e))


#==============主程序======================
if __name__=='__main__':
    index = spider()
    for r in index:
        data = [_.get_text() for _ in r('td')]
        Insert2servers(data)
