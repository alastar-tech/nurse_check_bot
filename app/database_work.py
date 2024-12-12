import time
import asyncio
from webbrowser import Error


class DBWork: #Класс для работы с БД, сейчас заточен под mySQL, в перспективе перейдем на PostgreSQL
    def __init__(self):
        import psycopg2 as pg2
        from config import db_conf

        try: self.connection = pg2.connect(user=db_conf['user'], password=db_conf['psw'], database=db_conf['database'], host=db_conf['host'], port=db_conf['port'])
        except Exception as e:
            print("Erorr while DBW:",e)
            self.succes_connect = False
        else: self.succes_connect = True


    def __read__(self, query):
        cursor = self.connection.cursor()
        #try: cursor.execute(query)
        #except: return ['запрос не дал результатов']
        #else: return list(cursor.fetchone())
        cursor.execute(query)
        return list(cursor.fetchone())

    def find_user(self, id):
        curs = self.connection.cursor()
        try: curs.execute(f"SELECT name FROM users WHERE tg_id=%s;",(id,))
        except Exception as e:
            return e
        else:
            r = curs.fetchall()
            if r == []:
                return False
            else:
                return r[0][0]
    def add_user(self, id, name):
        curs = self.connection.cursor()
        try: r = curs.execute(f"INSERT INTO users (tg_id, name) VALUES(%s,%s);",(id,name))
        except Exception as e:
            return e
        else:
            return True

    def logbook_add(self, id_user, attend, excuse_text=Null, excuse=Null, excuse_cat=Null,):
        curs = self.connection.cursor()
        try:
            r = curs.execute(f"INSERT INTO logbook (id_user, timestamp, attend, excuse_text) VALUES(%s,%s,%s,%s);", (id_user, time.localtime(), attend, excuse_text))
        except Exception as e:
            return e
        else:
            return True
'''
async def test():
    db = DBWork()
    text = db.find_user(123456)
    print(text)

if __name__ == "__main__":
    asyncio.run(test())
'''