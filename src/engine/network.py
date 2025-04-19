"""
Network module for the game engine.
"""

from components.datatypes import *

import socket
import threading
import sqlite3 as sql
from abc import ABC, abstractmethod
import json
import queue
from typing import Callable
import time



class Network(ABC):
    """
    Common network class for the client and server.
    """

    
    def __init__(self, address, port):
        self._packet_size = 1024

        self.port = port
        self.address = address
        self.__running = True
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._output_buffer = AdvancedDeque()
        self._input_buffer = AdvancedDeque()


    @property
    def address(self):
        """
        str - The address of the network.
        """
        return self.__address
    

    @address.setter
    def address(self, value):
        if isinstance(value, str):
            self.__address = value
        else:
            raise TypeError("Address must be a string:", value)


    @property
    def port(self):
        """
        int - The port of the network.
        """
        return self.__port
    

    @port.setter
    def port(self, value):
        if isinstance(value, int) and 0 <= value <= 65535:
            self.__port = value
        else:
            raise TypeError("Port must be an integer between 0 and 65535:", value)
        

    @property
    def running(self):
        """
        bool - True if the network is running, False otherwise.\n
        """
        return self.__running


    @staticmethod
    def _parse_data(data):
        try:
            decoded = data.decode("ascii")
            sep = chr(30)
            data_stream = decoded.split(sep)

            def convert(obj):
                if isinstance(obj, dict):
                    if obj.get("_type") == "Vector":
                        return Vector(obj["x"], obj["y"])
                    return {k: convert(v) for k, v in obj.items()}

                if isinstance(obj, (list, tuple)):
                    return [convert(item) for item in obj]

                return obj
            
            parsed_unordered = [convert(json.loads(data)) for data in data_stream]
            parsed_priority, parsed_not_priority = [], []
            for data_packet in parsed_unordered:
                has_priority, data = data_packet
                if has_priority:
                    parsed_priority.append(data)
                else:
                    parsed_not_priority.append(data)
            return parsed_priority, parsed_not_priority
            
        except json.JSONDecodeError as e:
            print(f"Error parsing data {data}: {e}")
            return ("", "")
    

    @staticmethod
    def _parse_for_send(has_priotity, cmd, data):
        class VectorEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Vector):
                    return {"_type": "Vector", "x": obj.x, "y": obj.y}
                return super().default(obj)

        payload = (has_priotity, (cmd, data))
        encoded = json.dumps(payload, cls=VectorEncoder)
        return encoded
    

    @abstractmethod
    def tick(self):
        pass


    def get_data(self, size = 1):
        """
        Called only by the engine.
        Returns the data from the input buffer.
        Args:
            size: The number of data to return.
        Returns:
            list[(str, any)] - The data from the input buffer.
        """
        return self._input_buffer.get_data(size)
    

    def stop(self):
        """
        Stops the network thread and closes the socket.
        """
        self.__running = False
        


#?ifdef CLIENT
class ClientNetwork(Network):
    """
    Network class for the client. It handles connection and authentication with the server.
    """


    def __init__(self, address: str, port: int):
        """
        Args:
            address: The address of the server.
            port: The port of the server.
        """
        super().__init__(address, port)
        
        self.socket.connect((self.address, self.port))

        self.__conn_thread = threading.Thread(target=self.__handle_connection)
        self.__conn_thread.daemon = True
        self.__conn_thread.start()

        self.__id = 0


    @property
    def connected(self):
        """
        bool - True if the client is connected to the server, False otherwise.\n
        """
        return self.socket is not None and self.socket.fileno() != -1


    @property
    def id(self):
        """
        int - The id of the client.\n
        If id is 0 or less, it can mean something of the following:
            0 -> The client is not yet connected to the server.
            -1 -> The client is connected to the server, but not yet registered.
            -2 -> The client is connected to the server, but the registration failed because the user already exists.
            -3 -> The client is connected to the server, but the registration failed because the username or password is invalid.
            -10 -> The client disconnected from the server.
        """
        return self.__id


    def send(self, cmd: str, data, has_priority = False):
        """
        Sends data to the client with the given id.
        Args:
            cmd: The command to send.
            data: The data to send.
            has_priority: If True, the data will be sent and processed first.
        """
        if has_priority:
            self._output_buffer.add_data_front(self._parse_for_send(has_priority, cmd, data))
            return
        
        self._output_buffer.add_data_back(self._parse_for_send(has_priority, cmd, data))


    def tick(self):
        """
        Called only by the engine.
        It ticks the network and sends all data in the output buffer to the server.
        """
        if not self.running:
            return
        
        data_buffer = self._output_buffer.get_all_data()
        if not data_buffer:
            return

        data = (chr(30).join(data_buffer) + chr(31)).encode("ascii")
        try:
            for i in range(0, len(data_buffer), self._packet_size):
                self.socket.send(data[i:i+self._packet_size])
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
            pass


    def __handle_connection(self):
        while self.running:
            data = b""
            try:
                while True:
                    data += self.socket.recv(self._packet_size + 28)
                    if data.endswith(chr(31).encode("ascii")):
                        data = data[:-1]
                        break
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
                print(f"Connection closed; {e}")
                break

            if not data:
                break

            priority_data, unpriority_data = self._parse_data(data)
            if self.id <= 0:
                for data in unpriority_data:
                    cmd, id = data
                    if cmd == "register_outcome":
                        self.__id = id
                        continue

            self._input_buffer.add_data_back_multiple(unpriority_data)
            self._input_buffer.add_data_front_multiple(priority_data)

        self.__id = -10
        self.socket.close()
        
#?endif



#?ifdef SERVER
class FakeConnection:
    """
    Helper class to simulate a connection.
    """
    
    
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address
        self.queue = queue.Queue()
        self.open = True


    def send(self, data):
        self.sock.sendto(data, self.address)


    def recv(self):
        if not self.open:
            return b""
        return self.queue.get()


    def close(self):
        self.open = False



class ServerNetwork(Network):
    """
    Network class for the server. It handles connection and authentication with the clients.
    It also handles the database connection and authentication.
    """

    def __init__(self, address: str, port: int, max_connections: int, on_connect: Callable[[int], None]):
        """
        Args:
            address: The address of the server.
            port: The port of the server.
            max_connections: The maximum number of connections allowed.
            on_connect:  A function that is called when a client connects to the server.
        """
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

        self.__connected_ids = set()

        self.__id_to_conn = {}
        self.__conn_to_id = {}
        self.__address_to_conn = {}
        

    @property
    def max_connections(self):
        """
        int - The maximum number of connections allowed.
        """
        return self.__max_connections


    @max_connections.setter
    def max_connections(self, value):
        if isinstance(value, int) and value > 0:
            self.__max_connections = value
        else:
            raise TypeError("Max connections must be a positive integer:", value)


    def send(self, id: int, cmd: str, data, has_priority = False):
        """
        Sends data to the client with the given id.
        Args:
            id: The id of the client to send data to.
            cmd: The command to send.
            data: The data to send.
            has_priority: If True, the data will be sent and processed first.
        """
        if has_priority:
            self._output_buffer.add_data_front((id, self._parse_for_send(has_priority, cmd, data)))
            return
        
        self._output_buffer.add_data_back((id, self._parse_for_send(has_priority, cmd, data)))


    def tick(self):
        """
        Called only by the engine.
        It ticks the network and sends all data in the output buffer to the clients.
        """
        if not self.running:
            return
        
        data_buffer = self._output_buffer.get_all_data()
        if not data_buffer:
            return
        
        data_buffer_by_id = {}
        for id, data in data_buffer:
            if id not in self.__id_to_conn:
                continue
            if id not in data_buffer_by_id:
                data_buffer_by_id[id] = []
            data_buffer_by_id[id].append(data)

        sep = chr(30).encode("ascii")
        end_sep = chr(31).encode("ascii")
        for id, data_list in data_buffer_by_id.items():
            short_data_list = []
            data_len = 0
            current_data = b""
            for data in data_list:
                data_len += len(data) + 1
                if data_len < 4 * self._packet_size or data_len == len(data) + 1:
                    current_data += data.encode("ascii") + sep
                else:
                    short_data_list.append(current_data[:-1] + end_sep)
                    current_data = data.encode("ascii") + sep
                    data_len = len(data) + 1
            if current_data:
                short_data_list.append(current_data[:-1] + end_sep)
                    
            conn = self.__id_to_conn[id]

            try:
                for data in short_data_list:
                    for i in range(0, len(data), self._packet_size):
                        if i > 0:
                            time.sleep(0.001)
                        conn.send(data[i:i+self._packet_size])
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
                self.__id_to_conn.pop(id)
                self.__conn_to_id.pop(conn)
                self.__address_to_conn.pop(conn.address)
                conn.close()
                print(f"Connection closed for id {id}")
                continue
        

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
            login_data = b""
            while True:
                login_data += conn.recv()
                if login_data.endswith(chr(31).encode("ascii")):
                    login_data = login_data[:-1]
                    break

            _, unporiority_data = self._parse_data(login_data)

            for data in unporiority_data:
                result = self.__handle_login(data, conn)
                if result:
                    break

            if result:
                self.__connected_ids.add(result)
                break
        
        self.__on_connect(self.__conn_to_id[conn])

        while self.running:
            data = b""
            try:
                while True:
                    data += conn.recv()
                    if data.endswith(chr(31).encode("ascii")):
                        data = data[:-1]
                        break
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                break

            if not data:
                continue

            priority_data, unporiority_data = self._parse_data(data)
            tagged_priority_data = [(self.__conn_to_id[conn], data) for data in priority_data]
            self._input_buffer.add_data_front_multiple(tagged_priority_data)
            tagged_unpriority_data = [(self.__conn_to_id[conn], data) for data in unporiority_data]
            self._input_buffer.add_data_back_multiple(tagged_unpriority_data)

        self.__connected_ids.remove(self.__conn_to_id[conn])
        self.__id_to_conn.pop(self.__conn_to_id[conn])
        self.__conn_to_id.pop(conn)
        conn.close()


    def __handle_login(self, login_data, conn):
        """
        Returns:
            If it retuturns a positive integer, it is the id of the user -> login was successful\n
            -1 -> User already logged in\n
            -2 -> User already exists\n
            -3 -> Invalid username or password
        """
        request, data = login_data
        username, password = data

        failed_registration_msg = lambda id: (self._parse_for_send(False, "register_outcome", id) + chr(31)).encode("ascii")

        match request:
            case "register":
                result = self.__register_user(username, password)
                if result == -1:
                    conn.send(failed_registration_msg(-2))
                    return False
                if result in self.__connected_ids:
                    conn.send(failed_registration_msg(-1))
                    return False
                self.__conn_to_id[conn] = result
                self.__id_to_conn[result] = conn
                self.send(result, "register_outcome", result)
                return True

            case "login":
                result = self.__login_user(username, password)
                if result == -1:
                    conn.send(failed_registration_msg(-3))
                    return False
                if result in self.__connected_ids:
                    conn.send(failed_registration_msg(-1))
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



