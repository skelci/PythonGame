import socket
import threading
import queue
import sqlite3 as sql
import ast
from abc import ABC, abstractmethod



class Network(ABC):
    def __init__(self, address, port):
        self.port = port
        self.address = address
        self.__running = True
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._output_queue = queue.Queue()
        self._input_queue = queue.Queue()

        sending_thread = threading.Thread(target=self._send_data)
        sending_thread.daemon = True
        sending_thread.start()


    @property
    def address(self):
        return self.__address
    

    @address.setter
    def address(self, value):
        if isinstance(value, str):
            self.__address = value
        else:
            raise TypeError("Address must be a string:", value)
        

    @property
    def port(self):
        return self.__port
    

    @port.setter
    def port(self, value):
        if isinstance(value, int) and 0 <= value <= 65535:
            self.__port = value
        else:
            raise TypeError("Port must be an integer between 0 and 65535:", value)
        

    @property
    def running(self):
        return self.__running


    def __parse_data(self, data):
        return ast.literal_eval(data.decode("ascii"))
    

    def __parse_for_send(self, cmd, data):
        return f"({cmd},{data})".encode("ascii")
    

    @abstractmethod
    def _send_data(self):
        pass


    def get_data(self):
        if not self._input_queue.empty():
            return self._input_queue.get()
    

    def stop(self):
        self.__running = False
        


#?ifdef CLIENT
class ClientNetwork(Network):
    def __init__(self, address, port):
        super().__init__(address, port)
        
        self.socket.connect((self.address, self.port))

        self.__conn_thread = threading.Thread(target=self.__handle_connection)
        self.__conn_thread.daemon = True
        self.__conn_thread.start()


    def send(self, cmd, data):
        self.__input_queue.put(self.__parse_for_send(cmd, data))


    def _send_data(self):
        while self.running:
            if not self._output_queue.empty():
                data = self._output_queue.get()
                self.socket.send(data)


    def __handle_connection(self):
        while self.running:
            data = self.socket.recv(1024)
            if not data:
                break
            self._output_queue.put(self.__parse_data(data))
        self.socket.close()
        
#?endif



#?ifdef SERVER
class ServerNetwork(Network):
    def __init__(self, address, port, max_connections, on_connect):
        super().__init__(address, port)
        self.max_connections = max_connections

        self.__on_connect = on_connect

        self.__db_conn = sql.connect("server.db")
        self.__db_cursor = self.__db_conn.cursor()
        self.__db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            )
        """)
        self.__db_conn.commit()

        self.socket.bind((self.address, self.port))
        self.socket.listen(self.max_connections)
        

        accept_thread = threading.Thread(target=self.__accept_connections)
        accept_thread.daemon = True
        accept_thread.start()

        self.__id_to_conn = {}
        self.__conn_to_id = {}
        

    @property
    def max_connections(self):
        return self.__max_connections


    @max_connections.setter
    def max_connections(self, value):
        if isinstance(value, int) and value > 0:
            self.__max_connections = value
        else:
            raise TypeError("Max connections must be a positive integer:", value)


    def send(self, id, cmd, data):
        self.__input_queue.put((id, self.__parse_for_send(cmd, data)))


    def _send_data(self):
        while self.running:
            if not self._output_queue.empty():
                id, data = self._output_queue.get()
                conn = self.__id_to_conn[id]
                conn.send(data)
        

    def __accept_connections(self):
        while self.running:
            conn, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.__handle_client, args=conn)
            client_thread.daemon = True
            client_thread.start()


    def __handle_client(self, conn):
        login_data = conn.recv(1024)
        while True:
            result = self.__handle_login(login_data, conn)
            if result:
                break

        self.__on_connect(self.__conn_to_id[conn])

        while self.running:
            data = conn.recv(1024)
            if not data:
                break
            self._output_queue.put((self.__conn_to_id[conn], data.decode("ascii")))

        self.__id_to_conn.pop(self.__conn_to_id[conn])
        self.__conn_to_id.pop(conn)
        conn.close()


    def __handle_login(self, login_data, conn):
        request, username, password = self.__parse_data(login_data)

        match request:
            case "register":
                result = self.__register_user(username, password)
                if result == -1:
                    conn.send(b"-1")
                    return False
                self.__conn_to_id[conn] = result
                self.__id_to_conn[result] = conn
                conn.send(str(result).encode("ascii"))
                return True

            case "login":
                result = self.__login_user(username, password)
                if result == -1:
                    conn.send(b"-1")
                    return False
                self.__conn_to_id[conn] = result
                self.__id_to_conn[result] = conn
                conn.send(str(result).encode("ascii"))
                return True

            case _:
                print("Invalid request:", request)


    def __register_user(self, username, password):
        if self.__db_cursor.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone() is not None:
            return -1
        
        self.__db_cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.__db_conn.commit()

        return self.__db_cursor.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()[0]
    

    def __login_user(self, username, password):
        user = self.__db_cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user is None:
            return -1
        
        return user[0]
        
#?endif



