import sqlite3, os
from typing import Union

SQL = os.path.expanduser('~/.Kiba/arcaea.db')
SONGSQL = os.path.join(os.path.dirname('src/static'), 'arcsong.db')

class arcsql():
    def __init__(self):
        os.makedirs(os.path.dirname(SQL), exist_ok=True)
        self.makesql()
        self.makelogin()
    
    def arc_conn(self):
        return sqlite3.connect(SQL)

    def song_conn(self):
        return sqlite3.connect(SONGSQL)

    def makesql(self):
        try:
            self.arc_conn().execute('''CREATE TABLE USER(
                ID          INTEGER     PRIMARY KEY     NOT NULL,
                QQID        INTEGER     NOT NULL,
                ARCID       TEXT        NOT NULL,
                ARCNAME     TEXT        NOT NULL,
                USER_ID     INTEGER,
                BIND_ID     INTEGER
            )''')
        except Exception as e:
            print(e)
    
    def makelogin(self):
        try:
            self.arc_conn().execute('''CREATE TABLE LOGIN(
                ID          INTEGER     PRIMARY KEY     NOT NULL,
                BIND_ID     INTEGER     NOT NULL,
                EMAIL       TEXT        NOT NULL,
                PASSWORD    TEXT        NOT NULL,
                IS_FULL     INTEGER     NOT NULL
            )''')
        except Exception as e:
            print(e)
    
    # 临时绑定账号
    def insert_temp_user(self, qqid, arcid, arcname):
        try:
            conn = self.arc_conn()
            conn.execute(f'INSERT INTO USER VALUES (NULL, {qqid}, "{arcid}", "{arcname.lower()}", NULL, NULL)')
            conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    # 正式绑定账号
    def insert_user(self, arcname, user_id, bind_id):
        try:
            conn = self.arc_conn()
            conn.execute(f'UPDATE USER SET ARCNAME = "{arcname}", USER_ID = {user_id}, BIND_ID = {bind_id} WHERE ARCNAME = "{arcname}"')
            conn.commit()
            self.__is_full__(bind_id)
            return True
        except Exception as e:
            return False

    def __is_full__(self, bind_id):
        try:
            info = self.arc_conn().execute(f'SELECT * FROM USER WHERE BIND_ID = {bind_id}').fetchall()
            if len(info) == 10:
                self.__update_is_full__(bind_id)
        except Exception as e:
            print(e)
    
    def __update_is_full__(self, bind_id):
        try:
            conn = self.arc_conn()
            conn.execute(f'UPDATE LOGIN SET IS_FULL = 1 WHERE BIND_ID = {bind_id}')
            conn.commit()
        except Exception as e:
            print(e)

    # 获取数据
    def get_bind_user(self, user_id) -> Union[tuple, bool]:
        '''
        使用 `user_id` 获取 `arcid` , `email` , `password`
        '''
        try:
            info = self.arc_conn().execute(f'SELECT ARCID, BIND_ID FROM USER WHERE USER_ID = {user_id}').fetchall()
            arcid, bind_id = info[0][0], info[0][1]
            email, pwd = self.__get_login__(bind_id)
            return arcid, email, pwd
        except Exception as e:
            return False
    
    def __get_login__(self, bind_id):
        try:
            result = self.arc_conn().execute(f'SELECT EMAIL, PASSWORD FROM LOGIN WHERE BIND_ID = {bind_id}').fetchall()
            return result[0][0], result[0][1]
        except Exception as e:
            return False

    # 获取查询用账号
    def get_not_full_email(self) -> Union[list, bool]:
        '''
        获取好友未满的查询用 `bind_id` , `email` , `password`
        '''
        try:
            result = self.arc_conn().execute(f'SELECT BIND_ID, EMAIL, PASSWORD FROM LOGIN WHERE IS_FULL = 0').fetchall()
            if not result:
                return False
            else:
                return result[0]
        except Exception as e:
            return False

    # 获取好友码和user_id
    def get_user(self, qqid) -> Union[list, bool]:
        '''
        使用QQ号 `qqid` 获取好友码 `arcid` 和 `user_id`
        '''
        try:
            result = self.arc_conn().execute(f'SELECT ARCID, USER_ID FROM USER WHERE QQID = {qqid}').fetchall()
            if not result:
                return False
            else:
                return result[0]
        except Exception as e:
            return False
    
    # 获取游戏名
    def get_user_name(self, user_id):
        '''
        使用 `user_id` 获取游戏名 `arcname`
        '''
        try:
            result = self.arc_conn().execute(f'SELECT ARCNAME FROM USER WHERE USER_ID = {user_id}').fetchall()
            return result
        except Exception as e:
            return False

    # 获取user_id
    def get_user_code(self, arcid):
        '''
        使用好友码 `arcid` 获取 `user_id`
        '''
        try:
            result = self.arc_conn().execute(f'SELECT USER_ID FROM USER WHERE ARCID = "{arcid}"').fetchall()
            if not result:
                return False
            else:
                return result[0]
        except Exception as e:
            return False

    # 删除账号
    def delete_user(self, qqid):
        try:
            conn = self.arc_conn()
            conn.execute(f'DELETE FROM USER WHERE QQID = {qqid}')
            conn.commit()
            return True
        except Exception as e:
            return False

    # 查询歌曲
    def song_info(self, songid, diff):
        try:
            result = self.song_conn().execute(f'select name_en, name_jp, artist, {diff} from song where songid = "{songid}"').fetchall()
            if not result:
                return False
            else:
                return result[0]
        except Exception as e:
            return False
