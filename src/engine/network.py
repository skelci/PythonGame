from components.datatypes import *

import socket
import threading
import queue
import sqlite3 as sql
from abc import ABC, abstractmethod
import json



class Network(ABC):
    def __init__(self, address, port):
        self.port = port
        self.address = address
        self.__running = True
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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


    @staticmethod
    def _parse_data(data):
        try:
            decoded = data.decode("ascii")
            parsed = json.loads(decoded)

            def convert(obj):
                if isinstance(obj, dict):
                    if obj.get("_type") == "Vector":
                        return Vector(obj["x"], obj["y"])
                    return {k: convert(v) for k, v in obj.items()}

                if isinstance(obj, (list, tuple)):
                    return [convert(item) for item in obj]

                return obj

            return convert(parsed)
        except Exception as e:
            print(f"Error parsing data {data}: {e}")
            return ("", "")
    

    @staticmethod
    def _parse_for_send(cmd, data):
        class VectorEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Vector):
                    return {"_type": "Vector", "x": obj.x, "y": obj.y}
                return super().default(obj)

        payload = (cmd, data)
        encoded = json.dumps(payload, cls=VectorEncoder)
        return encoded.encode("ascii")
    

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

        self.__id = -1


    @property
    def id(self):
        return self.__id


    def send(self, cmd, data):
        self._output_queue.put(self._parse_for_send(cmd, data))


    def _send_data(self):
        while self.running:
            if not self._output_queue.empty():
                data = self._output_queue.get()
                try:
                    self.socket.send(data)
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                    break


    def __handle_connection(self):
        while self.running:
            data = None
            try:
                data = self.socket.recv(1024)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                break

            if not data:
                break

            parsed_data = self._parse_data(data)
            if self.id == -1:
                cmd, id = parsed_data
                if cmd == "register_outcome":
                    self.__id = id
                    continue

            self._input_queue.put(parsed_data)

        self.__id = -1
        self.socket.close()
        
#?endif



#?ifdef SERVER
class FakeConnection:
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address
        self.queue = queue.Queue()
        self.open = True


    def send(self, data):
        self.sock.sendto(data, self.address)


    def recv(self, size):
        if not self.open:
            return b""
        return self.queue.get()


    def close(self):
        self.open = False



class ServerNetwork(Network):
    def __init__(self, address, port, max_connections, on_connect):
        super().__init__(address, port)
        self.max_connections = max_connections

        self.__on_connect = on_connect

        self.__db_conn = sql.connect("server.db", check_same_thread=False)
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

        accept_thread = threading.Thread(target=self.__accept_connections)
        accept_thread.daemon = True
        accept_thread.start()

        self.__id_to_conn = {}
        self.__conn_to_id = {}
        self.__address_to_conn = {}
        

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
        self._output_queue.put((id, self._parse_for_send(cmd, data)))


    def _send_data(self):
        while self.running:
            if not self._output_queue.empty():
                id, data = self._output_queue.get()
                if not id in self.__id_to_conn:
                    continue
                conn = self.__id_to_conn[id]
                try:
                    conn.send(data)
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                    break
        

    def __accept_connections(self):
        while self.running:
            try:
                data, address = self.socket.recvfrom(1024)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                break
            if address not in self.__address_to_conn:
                conn = FakeConnection(self.socket, address)
                self.__address_to_conn[address] = conn
                client_thread = threading.Thread(target=self.__handle_client, args=(conn,))
                client_thread.daemon = True
                client_thread.start()
            self.__address_to_conn[address].queue.put(data)


    def __handle_client(self, conn):
        while True:
            login_data = conn.recv(1024)
            parsed_data = self._parse_data(login_data)

            result = self.__handle_login(parsed_data, conn)
            if result:
                break

        self.__on_connect(self.__conn_to_id[conn])

        while self.running:
            try:
                data = conn.recv(1024)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                break

            if not data:
                break

            parsed_data = self._parse_data(data)
            self._input_queue.put((self.__conn_to_id[conn], parsed_data))

        self.__id_to_conn.pop(self.__conn_to_id[conn])
        self.__conn_to_id.pop(conn)
        conn.close()


    def __handle_login(self, login_data, conn):
        request, data = login_data
        username, password = data

        match request:
            case "register":
                result = self.__register_user(username, password)
                if result == -1:
                    conn.send(b"('register_outcome',-1)")
                    return False
                self.__conn_to_id[conn] = result
                self.__id_to_conn[result] = conn
                self.send(result, "register_outcome", result)
                return True

            case "login":
                result = self.__login_user(username, password)
                if result == -1:
                    conn.send(b"('register_outcome',-1)")
                    return False
                self.__conn_to_id[conn] = result
                self.__id_to_conn[result] = conn
                self.send(result, "register_outcome", result)
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



