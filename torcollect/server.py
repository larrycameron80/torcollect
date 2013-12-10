import torcollect.database


class LoginType:
    PASSWORD = 0
    PUBLICKEY = 1


class Server(object):
    def __init__(self):
        #server-information
        self.id = None
        self.ip = ""
        self.name = ""
        #auth-information
        self.login_type = None
        self.port = 22
        self.username = ""
        self.password = ""
        self.keyfile = ""

    def get_name(self):
        return self.name

    def get_ip(self):
        return self.ip

    @classmethod
    def load(cls, address):
        db = torcollect.database.Database()
        cur = db.cursor()
        stmnt = "SELECT SRV_ID, SRV_NAME, LGI_AUTHTYPE, LGI_SSHPORT, \
                 LGI_USER, LGI_PASSWORD, LGI_KEYFILE \
                 FROM Server INNER JOIN Login \
                   ON (LGI_SRV_ID = SRV_ID) \
                 WHERE SRV_IP = %(address)s;"
        cur.execute(stmnt, {"address": address})
        res = cur.fetchone()
        server = Server()
        server.id = res[0]
        server.ip = address
        server.name= res[1]
        server.login_type = res[2]
        server.port = res[3]
        server.username = res[4]
        server.password = res[5]
        server.keyfile = res[6]
        return server

    @classmethod
    def create(cls, address, name, port, user, password, keyfile):
        server = Server()
        server.ip = address
        server.name = name
        server.port = port
        server.username = user
        server.password = password
        if keyfile is not None:
            server.login_type = LoginType.PUBLICKEY
            server.keyfile = keyfile
        else:
            server.login_type = LoginType.PASSWORD
        return server

    @classmethod
    def get_server_list(cls):
        db = torcollect.database.Database()
        cur = db.cursor()
        stmnt = "SELECT SRV_NAME, SRV_IP FROM Server;"
        cur.execute(stmnt)
        ret = []
        for name, ip in cur.fetchall():
            srv = Server()
            srv.ip = ip
            srv.name = name
            ret.append(srv)
        return ret

    def store(self):
        db = torcollect.database.Database()
        cur = db.cursor()
        if self.id is None:
            stmnt = "INSERT INTO Server (SRV_IP, SRV_NAME)\
                     VALUES (%(ip)s,%(name)s) RETURNING SRV_ID;"
            cur.execute(stmnt, {'ip': self.ip, 'name': self.name})
            self.id = cur.fetchone()[0]

            if self.login_type == LoginType.PASSWORD:
                stmnt = "INSERT INTO Login (LGI_AUTHTYPE, LGI_SSHPORT,\
                         LGI_USER, LGI_PASSWORD, LGI_SRV_ID) \
                         VALUES (%(auth)d, %(ssh)d,\
                         %(user)s, %(pw)s, %(srv_id)d);"
                cur.execute(stmnt, {'auth': self.login_type,
                                    'ssh': self.port,
                                    'user': self.username,
                                    'pw': self.password,
                                    'srv_id': self.id})
            elif self.login_type == LoginType.PUBLICKEY:
                # TODO: PublicKey File can only be a textfile by now
                #       Don't know whether binary keyfiles will be needed
                #       In the future
                stmnt = "INSERT INTO Login (LGI_AUTHTYPE, LGI_SSHPORT,\
                         LGI_USER, LGI_PASSWORD, LGI_KEYFILE, LGI_SRV_ID) \
                        VALUES  (%(auth)d, %(ssh)d, %(user)s, %(pw)s, \
                        %(keyfile)s, %(srv_id)d);"
                cur.execute(stmnt, {'auth': self.login_type,
                                    'ssh': self.port,
                                    'user': self.username,
                                    'pw': self.password,
                                    'keyfile': self.keyfile,
                                    'srv_id' : self.id})
        else:
            stmnt = "UPDATE SERVER SET SRV_NAME = %(name)s, SRV_IP = %(ip)s\
                     WHERE SRV_ID = %(id)d;"
            cur.execute(stmnt,
                        {'ip': self.ip, 'name': self.name, 'id': self.id})
        db.commit()

    def delete(self):
        db = torcollect.database.Database()
        cur = db.cursor()
        stmnt = "DELETE FROM Server WHERE SRV_ID = %(id)d;"
        cur.execute(stmnt, {'id': self.id})
        db.commit()
