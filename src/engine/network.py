"""
Network module for the game engine.
Uses TCP for reliable non-priority messages and UDP for fast priority messages.
"""

from components.datatypes import *

import socket
import threading
import sqlite3 as sql
from abc import ABC, abstractmethod
import json
from typing import Callable, List, Tuple, Any, Dict
import time



RECORD_SEPARATOR = chr(30)
END_OF_MESSAGE_SEPARATOR = chr(31)
RECORD_SEPARATOR_BYTES = RECORD_SEPARATOR.encode("ascii")
END_OF_MESSAGE_SEPARATOR_BYTES = END_OF_MESSAGE_SEPARATOR.encode("ascii")



class Network(ABC):
    """
    Common network class for the client and server.
    Handles data parsing and buffering.
    """

    def __init__(self, address, port):
        self._packet_size = 4096

        self.port = port
        self.address = address
        self._running = True

        self._receive_priority_buffer = AdvancedQueue()
        self._receive_unpriority_buffer = AdvancedQueue()
        self._send_priority_buffer = AdvancedQueue()
        self._send_unpriority_buffer = AdvancedQueue()


    @property
    def address(self):
        """ str - The address of the network. """
        return self.__address


    @address.setter
    def address(self, value):
        if isinstance(value, str):
            self.__address = value
        else:
            raise TypeError("Address must be a string:", value)


    @property
    def port(self):
        """ int - The port of the network (UDP port for server/client). TCP uses port + 1. """
        return self.__port


    @port.setter
    def port(self, value):
        if isinstance(value, int) and 0 <= value <= 65535 - 1:
            self.__port = value
        else:
            raise TypeError("Port must be an integer between 0 and 65535 - 1 (TCP port uses port + 1):", value)


    @property
    def running(self):
        """ bool - True if the network is running, False otherwise. """
        return self._running


    @staticmethod
    def _parse_data(data: bytes) -> List[Tuple[bool, Any]]:
        """ Parses a raw byte stream potentially containing multiple messages """
        parsed_data = []
        try:
            if data.endswith(END_OF_MESSAGE_SEPARATOR_BYTES):
                data = data[:-1]

            decoded = data.decode("ascii")
            data_stream = decoded.split(RECORD_SEPARATOR)

            def convert(obj):
                if isinstance(obj, dict):
                    if obj.get("_type") == "Vector":
                        return Vector(obj["x"], obj["y"])
                    return {k: convert(v) for k, v in obj.items()}

                if isinstance(obj, (list, tuple)):
                    return [convert(item) for item in obj]

                return obj

            for json_str in data_stream:
                if not json_str:
                    continue

                payload = convert(json.loads(json_str))
                parsed_data.append(payload)

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Error parsing data chunk: {e} (Data: {data[:100]}...)")
        except Exception as e:
            print(f"Unexpected error parsing data: {e} (Data: {data[:100]}...)")
        return parsed_data


    @staticmethod
    def _parse_for_send(cmd: str, data: Any) -> str:
        class VectorEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Vector):
                    return {"_type": "Vector", "x": obj.x, "y": obj.y}
                return super().default(obj)

        payload = (cmd, data)
        encoded = json.dumps(payload, cls=VectorEncoder)
        return encoded


    @abstractmethod
    def tick(self):
        """ Processes output buffers and sends data over appropriate sockets. """
        pass


    def get_data(self, size=1) -> List[Any]:
        """
        Called only by the engine.
        Returns the data from the input buffer.
        """
        data = self._receive_priority_buffer.get_all_data()
        data += self._receive_unpriority_buffer.get_data(size)
        return data


    @abstractmethod
    def stop(self):
        """ Stops network threads and closes sockets. """
        self._running = False



#?ifdef CLIENT
class ClientNetwork(Network):
    """
    Network class for the client. Uses TCP for login and non-priority data,
    UDP for priority data.
    """

    def __init__(self, address: str, port: int):
        """
        Args:
            address: The address of the server.
            port: The UDP port of the server. TCP port will be port + 1.
        """
        super().__init__(address, port)
        self.tcp_port = self.port + 1

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_conn_thread = None
        self.udp_recv_thread = None
        self.__id = 0
        self.__server_ip = None

        try:
            print(f"[Client] Connecting TCP to {self.address}:{self.tcp_port}")
            self.tcp_socket.connect((self.address, self.tcp_port))
            self.__server_ip = self.tcp_socket.getpeername()[0]
            print(f"[Client] TCP Connected to {self.__server_ip}:{self.tcp_port}.")

            self.tcp_conn_thread = threading.Thread(target=self.__handle_tcp_connection, daemon=True)
            self.tcp_conn_thread.start()

            self.udp_recv_thread = threading.Thread(target=self.__handle_udp_connection, daemon=True)

        except socket.error as e:
            print(f"[Client] Failed to connect TCP socket: {e}")
            self.__id = -10
            self.stop()


    @property
    def connected(self):
        """ bool - True if the TCP socket is connected, False otherwise. """
        try:
            # fileno() raises OSError if closed, or returns -1 if not valid
            return self.tcp_socket and self.tcp_socket.fileno() != -1
        except OSError:
            return False


    @property
    def id(self):
        """
        int - The id of the client.\n
        If id is 0 or less, it can mean something of the following:
            0 -> TCP connected, attempting login/registration.
            >0 -> Login/Registration successful.
            -1 -> (Server-side meaning, client shouldn't see this directly often)
            -2 -> Registration failed: user already exists.
            -3 -> Login failed: invalid credentials.
            -10 -> Disconnected or connection failed.
        """
        return self.__id


    def send(self, cmd: str, data, has_priority=False):
        """
        Adds data to the output buffer to be sent on the next tick.
        Args:
            cmd: The command to send.
            data: The data to send.
            has_priority: If True, data will be sent via UDP; otherwise via TCP.
        """
        if not self.running:
            return
        parsed_data = self._parse_for_send(cmd, data)
        
        if has_priority:
            self._send_priority_buffer.add_data(parsed_data)
        else:
            self._send_unpriority_buffer.add_data(parsed_data)


    def tick(self):
        """
        Called only by the engine.
        Sends data from the output buffer via UDP (priority) or TCP (non-priority).
        """
        if not self.running or not self.connected:
            return

        udp_payloads = self._send_priority_buffer.get_all_data()
        tcp_payloads = self._send_unpriority_buffer.get_all_data()

        if udp_payloads:
            try:
                full_udp_message = (RECORD_SEPARATOR.join(udp_payloads) + END_OF_MESSAGE_SEPARATOR).encode('ascii')
                self.udp_socket.sendto(full_udp_message, (self.address, self.port))
            except socket.error as e:
                print(f"[Client] UDP send error: {e}")
            except Exception as e:
                 print(f"[Client] Error encoding/sending UDP data: {e}")

        if tcp_payloads:
            try:
                full_tcp_message = (RECORD_SEPARATOR.join(tcp_payloads) + END_OF_MESSAGE_SEPARATOR).encode('ascii')
                self.tcp_socket.sendall(full_tcp_message)
            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                print(f"[Client] TCP send error (connection lost): {e}")
                self.stop()
            except Exception as e:
                print(f"[Client] Error encoding/sending TCP data: {e}")


    def __handle_tcp_connection(self):
        """ Handles receiving data from the TCP connection. """
        buffer = b""
        while self.running:
            try:
                data = self.tcp_socket.recv(self._packet_size)
                if not data:
                    print("[Client] TCP connection closed by server.")
                    break

                buffer += data

                while END_OF_MESSAGE_SEPARATOR_BYTES in buffer:
                    message, buffer = buffer.split(END_OF_MESSAGE_SEPARATOR_BYTES, 1)
                    parsed_packets = self._parse_data(message + END_OF_MESSAGE_SEPARATOR_BYTES) # Add back separator for parsing logic

                    unpriority_data = []
                    for payload in parsed_packets:
                        unpriority_data.append(payload)
                        cmd, response_data = payload
                        if cmd != "register_outcome":
                            continue
                        
                        old_id = self.__id
                        self.__id = response_data
                        print(f"[Client] Received register_outcome: {self.__id}")
                        if old_id > 0 or self.__id <= 0:
                            continue
                        
                        print(f"[Client] Login successful (ID: {self.__id}). Registering UDP.")
                        udp_reg_msg = self._parse_for_send("register_udp", self.__id)
                        full_udp_message = (udp_reg_msg + END_OF_MESSAGE_SEPARATOR).encode('ascii')
                        try:
                            self.udp_socket.sendto(full_udp_message, (self.address, self.port))
                            print("[Client] Sent UDP registration.")
                            # Start the UDP receiving thread only after the first send
                            if self.udp_recv_thread and not self.udp_recv_thread.is_alive():
                                print("[Client] Starting UDP receive thread.")
                                self.udp_recv_thread.start()
                        except socket.error as e:
                            print(f"[Client] Failed to send UDP registration: {e}")
                        except Exception as e:
                            print(f"[Client] Error encoding/sending UDP registration: {e}")

                    self._receive_unpriority_buffer.add_data_multiple(unpriority_data)

            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
                print(f"[Client] TCP connection error (connection lost): {e}")
                break
            except Exception as e:
                print(f"[Client] Unexpected error in TCP handler: {e}")
                break

        print("[Client] TCP connection handler stopped.")
        self.stop()


    def __handle_udp_connection(self):
        """ Handles receiving data from the UDP socket. """
        while self.running and self.__server_ip is None:
            time.sleep(0.01)

        if not self.running: return

        expected_server_addr = (self.__server_ip, self.port)

        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(self._packet_size)
                if not data:
                    continue

                if addr != expected_server_addr:
                    print(f"[Client] Received UDP from unexpected source {addr}. Expected {expected_server_addr}. Ignoring.")
                    continue

                parsed_packets = self._parse_data(data)

                priority_data = []
                for payload in parsed_packets:
                    priority_data.append(payload)

                self._receive_priority_buffer.add_data_multiple(priority_data)

            except socket.error as e:
                if self.running:
                    print(f"[Client] UDP receive error: {e}")
                break
            except Exception as e:
                print(f"[Client] Unexpected error in UDP handler: {e}")
                break

        print("[Client] UDP connection handler stopped.")


    def stop(self):
        """ Stops the network threads and closes sockets. """
        if not self._running:
            return
        print("[Client] Stopping network...")
        self._running = False

        if self.tcp_socket:
            try:
                self.tcp_socket.shutdown(socket.SHUT_RDWR)
            except (OSError, socket.error):
                pass
            finally:
                self.tcp_socket.close()
                self.tcp_socket = None

        if self.udp_socket:
            try:
                self.udp_socket.close()
                self.udp_socket = None
            except socket.error:
                pass

        self.__id = -10
        print("[Client] Network stopped.")

#?endif


#?ifdef SERVER
class ServerNetwork(Network):
    """
    Network class for the server. Handles TCP connections for login/non-priority data
    and UDP for priority data.
    """

    def __init__(self, address: str, port: int, max_connections: int, on_connect: Callable[[int], None], on_disconnect: Callable[[int], None] = None):
        """
        Args:
            address: The address of the server.
            port: The UDP port for the server. TCP port will be port + 1.
            max_connections: The maximum number of TCP connections allowed.
            on_connect: A function called when a client successfully connects and logs in (passes client ID).
            on_disconnect: A function called when a client disconnects (passes client ID).
        """
        super().__init__(address, port)
        self.tcp_port = self.port + 1
        self.max_connections = max_connections
        self.__on_connect = on_connect
        self.__on_disconnect = on_disconnect

        self.__db_conn = sql.connect("server.db", check_same_thread=False)
        self.__db_cursor = self.__db_conn.cursor()
        self.__db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        self.__db_conn.commit()

        self.__id_to_tcp_conn: Dict[int, socket.socket] = {}
        self.__tcp_conn_to_id: Dict[socket.socket, int] = {}
        self.__id_to_udp_addr: Dict[int, tuple] = {}
        self.__udp_addr_to_id: Dict[tuple, int] = {}
        self.__connected_ids = set()

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.udp_socket.bind((self.address, self.port))
            print(f"[Server] UDP Socket bound to {self.address}:{self.port}")
        except socket.error as e:
            print(f"[Server] Failed to bind UDP socket: {e}")
            raise

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow address reuse
        try:
            self.tcp_socket.bind((self.address, self.tcp_port))
            self.tcp_socket.listen(self.max_connections)
            print(f"[Server] TCP Socket listening on {self.address}:{self.tcp_port}")
        except socket.error as e:
            print(f"[Server] Failed to bind/listen TCP socket: {e}")
            self.udp_socket.close()
            raise

        self.tcp_accept_thread = threading.Thread(target=self.__accept_tcp_connections, daemon=True)
        self.udp_read_thread = threading.Thread(target=self.__handle_udp_reads, daemon=True)

        self.tcp_accept_thread.start()
        self.udp_read_thread.start()


    @property
    def max_connections(self):
        """ int - The maximum number of TCP connections allowed. """
        return self.__max_connections


    @max_connections.setter
    def max_connections(self, value):
        if isinstance(value, int) and value > 0:
            self.__max_connections = value
            if hasattr(self, 'tcp_socket') and self.tcp_socket:
                self.tcp_socket.listen(value)
        else:
            raise TypeError("Max connections must be a positive integer:", value)


    def send(self, client_id: int, cmd: str, data, has_priority=False):
        """
        Adds data to the output buffer to be sent to a specific client on the next tick.
        Args:
            client_id: The ID of the client to send data to.
            cmd: The command to send.
            data: The data to send.
            has_priority: If True, data will be sent via UDP; otherwise via TCP.
        """
        if not self.running:
            return

        if client_id not in self.__connected_ids:
            return

        parsed_data = self._parse_for_send(cmd, data)
        if has_priority:
            if client_id in self.__id_to_udp_addr:
                self._send_priority_buffer.add_data((client_id, parsed_data))
            else:
                print(f"Server Warning: No UDP address for client {client_id}. Cannot send priority message '{cmd}'.")
        else:
            if client_id in self.__id_to_tcp_conn:
                self._send_unpriority_buffer.add_data((client_id, parsed_data))
            else:
                print(f"Server Warning: No TCP connection for client {client_id}. Cannot send non-priority message '{cmd}'.")


    def tick(self):
        """
        Called only by the engine.
        Sends data from the output buffer to clients via UDP (priority) or TCP (non-priority).
        """
        if not self.running:
            return
        
        udp_payloads = self._send_priority_buffer.get_all_data()
        tcp_payloads = self._send_unpriority_buffer.get_all_data()

        data_by_client_udp = {}
        data_by_client_tcp = {}

        for client_id, parsed_data in udp_payloads:
            data_by_client_udp.setdefault(client_id, []).append(parsed_data)
        for client_id, parsed_data in tcp_payloads:
            data_by_client_tcp.setdefault(client_id, []).append(parsed_data)

        for client_id, payloads in data_by_client_udp.items():
            udp_addr = self.__id_to_udp_addr.get(client_id)
            if not udp_addr or not payloads:
                continue

            current_batch = []
            current_batch_size = len(END_OF_MESSAGE_SEPARATOR_BYTES)

            for payload in payloads:
                try:
                    payload_bytes = payload.encode('ascii')
                except UnicodeEncodeError as e:
                    print(f"Server Warning: Cannot encode UDP payload for client {client_id}: {e}. Skipping payload.")
                    continue

                payload_len = len(payload_bytes)
                separator_len = len(RECORD_SEPARATOR_BYTES) if current_batch else 0

                if payload_len + separator_len + len(END_OF_MESSAGE_SEPARATOR_BYTES) > self._packet_size:
                    print(f"Server Warning: Single UDP payload for client {client_id} is too large ({payload_len} bytes). Skipping.")
                    if current_batch:
                        try:
                            batch_message = (RECORD_SEPARATOR.join(current_batch) + END_OF_MESSAGE_SEPARATOR).encode('ascii')
                            self.udp_socket.sendto(batch_message, udp_addr)
                        except socket.error as e:
                            print(f"[Server] UDP send error (pre-large payload batch) to {udp_addr} (ID: {client_id}): {e}")
                            current_batch = []
                            break
                        except Exception as e:
                            print(f"[Server] Error encoding/sending UDP batch (pre-large) to {udp_addr} (ID: {client_id}): {e}")
                            current_batch = []
                            break
                        current_batch = []
                        current_batch_size = len(END_OF_MESSAGE_SEPARATOR_BYTES)
                    continue

                if current_batch_size + separator_len + payload_len > self._packet_size:
                    try:
                        batch_message = (RECORD_SEPARATOR.join(current_batch) + END_OF_MESSAGE_SEPARATOR).encode('ascii')
                        self.udp_socket.sendto(batch_message, udp_addr)
                    except socket.error as e:
                        print(f"[Server] UDP send error (batch) to {udp_addr} (ID: {client_id}): {e}")
                        current_batch = []
                        break
                    except Exception as e:
                        print(f"[Server] Error encoding/sending UDP batch to {udp_addr} (ID: {client_id}): {e}")
                        current_batch = []
                        break

                    current_batch = [payload]
                    current_batch_size = len(END_OF_MESSAGE_SEPARATOR_BYTES) + payload_len
                else:
                    current_batch.append(payload)
                    current_batch_size += separator_len + payload_len

            if not current_batch:
                continue
            try:
                batch_message = (RECORD_SEPARATOR.join(current_batch) + END_OF_MESSAGE_SEPARATOR).encode('ascii')
                self.udp_socket.sendto(batch_message, udp_addr)
            except socket.error as e:
                print(f"[Server] UDP send error (final batch) to {udp_addr} (ID: {client_id}): {e}")
            except Exception as e:
                print(f"[Server] Error encoding/sending final UDP batch to {udp_addr} (ID: {client_id}): {e}")

        disconnected_clients = []
        for client_id, payloads in data_by_client_tcp.items():
            tcp_conn = self.__id_to_tcp_conn.get(client_id)
            if tcp_conn and payloads:
                try:
                    full_tcp_message = (RECORD_SEPARATOR.join(payloads) + END_OF_MESSAGE_SEPARATOR).encode('ascii')
                    tcp_conn.sendall(full_tcp_message)
                except (BrokenPipeError, ConnectionResetError, OSError) as e:
                    print(f"[Server] TCP send error to client {client_id} (connection lost): {e}")
                    disconnected_clients.append(client_id)
                except Exception as e:
                    print(f"[Server] Error encoding/sending TCP to client {client_id}: {e}")
                    disconnected_clients.append(client_id)

        for client_id in disconnected_clients:
            self.__cleanup_client(client_id)


    def __accept_tcp_connections(self):
        """ Accepts incoming TCP connections and starts a handler thread for each. """
        while self.running:
            try:
                conn, addr = self.tcp_socket.accept()
                print(f"[Server] Accepted TCP connection from {addr}")

                if len(self.__connected_ids) >= self.max_connections:
                    print(f"[Server] Max connections ({self.max_connections}) reached. Rejecting {addr}.")
                    conn.close()
                    continue

                client_thread = threading.Thread(target=self.__handle_client_tcp, args=(conn, addr), daemon=True)
                client_thread.start()

            except socket.error as e:
                if self.running:
                    print(f"[Server] Error accepting TCP connections: {e}")
                break
            except Exception as e:
                 print(f"[Server] Unexpected error in TCP accept loop: {e}")


    def __handle_client_tcp(self, conn: socket.socket, addr: tuple):
        """ Handles login, registration, and non-priority data for a single TCP client. """
        client_id = 0
        buffer = b""

        try:
            while self.running and client_id == 0:
                data = conn.recv(self._packet_size)
                if not data:
                    print(f"[Server] Client {addr} disconnected before login.")
                    conn.close()
                    return

                buffer += data
                while END_OF_MESSAGE_SEPARATOR_BYTES in buffer:
                    message, buffer = buffer.split(END_OF_MESSAGE_SEPARATOR_BYTES, 1)
                    parsed_packets = self._parse_data(message + END_OF_MESSAGE_SEPARATOR_BYTES)

                    for payload in parsed_packets:
                        # Expecting ('register', (user, pass)) or ('login', (user, pass))
                        cmd, login_data = payload
                        result_id = self.__handle_login(cmd, login_data, conn)

                        if result_id > 0:
                            client_id = result_id
                            if client_id in self.__connected_ids:
                                print(f"[Server] User ID {client_id} (from {addr}) is already connected. Disconnecting duplicate.")
                                self.send(client_id, "register_outcome", -1)
                                time.sleep(0.1)
                                conn.close()
                                return

                            self.__id_to_tcp_conn[client_id] = conn
                            self.__tcp_conn_to_id[conn] = client_id
                            self.__connected_ids.add(client_id)
                            print(f"[Server] Client {addr} logged in as ID {client_id}.")
                            self.send(client_id, "register_outcome", client_id)
                            self.__on_connect(client_id)
                            break
                        else:
                            self.send(client_id, "register_outcome", result_id)
                            fail_msg = self._parse_for_send("register_outcome", result_id)
                            full_fail_msg = (fail_msg + END_OF_MESSAGE_SEPARATOR).encode('ascii')
                            conn.sendall(full_fail_msg)
                            break
                    if client_id > 0:
                        break

            while self.running and client_id > 0:
                data = conn.recv(self._packet_size)
                if not data:
                    print(f"[Server] Client {client_id} (TCP) disconnected.")
                    break

                buffer += data
                while END_OF_MESSAGE_SEPARATOR_BYTES in buffer:
                    message, buffer = buffer.split(END_OF_MESSAGE_SEPARATOR_BYTES, 1)
                    parsed_packets = self._parse_data(message + END_OF_MESSAGE_SEPARATOR_BYTES)

                    unpriority_packets = []
                    for payload in parsed_packets:
                        unpriority_packets.append((client_id, payload))

                    self._receive_unpriority_buffer.add_data_multiple(unpriority_packets)

        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"[Server] TCP connection error with client {client_id if client_id > 0 else addr}: {e}")
        except Exception as e:
            print(f"[Server] Unexpected error in TCP handler for {client_id if client_id > 0 else addr}: {e}")
        finally:
            if client_id > 0:
                self.__cleanup_client(client_id)
            else:
                try:
                    conn.close()
                except: pass
            print(f"[Server] TCP handler stopped for {client_id if client_id > 0 else addr}.")


    def __handle_udp_reads(self):
        """ Handles receiving all incoming UDP datagrams. """
        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(self._packet_size)
                if not data:
                    continue

                parsed_packets = self._parse_data(data)
                client_id = self.__udp_addr_to_id.get(addr)

                priority_packets = []

                for payload in parsed_packets:
                    cmd, packet_data = payload

                    if cmd == "register_udp":
                        reg_id = packet_data
                        if reg_id in self.__id_to_tcp_conn and reg_id not in self.__id_to_udp_addr:
                            print(f"[Server] Registered UDP address {addr} for client ID {reg_id}.")
                            self.__id_to_udp_addr[reg_id] = addr
                            self.__udp_addr_to_id[addr] = reg_id
                            client_id = reg_id
                        else:
                            print(f"Server Warning: Received UDP registration for unknown/already registered ID {reg_id} from {addr}.")
                        continue

                    if client_id is not None:
                        priority_packets.append((client_id, payload))
                    else:
                        print(f"[Server] Received UDP from unknown address {addr}. Ignoring data.")

                if client_id is not None:
                    self._receive_priority_buffer.add_data_multiple(priority_packets)

            except socket.error as e:
                if self.running:
                    print(f"[Server] UDP receive error: {e}")
                break
            except Exception as e:
                print(f"[Server] Unexpected error in UDP read loop: {e}")


    def __handle_login(self, request: str, data: tuple, conn: socket.socket) -> int:
        """
        Handles 'register' or 'login' requests received via TCP.
        Returns:
            Positive int: User ID on success.
            -1: User already logged in (checked later in handler).
            -2: Registration failed: username exists.
            -3: Login failed: invalid username/password.
            0: Invalid request type.
        """
        try:
            username, password = data
        except (TypeError, ValueError):
            print(f"[Server] Invalid login data format from {conn.getpeername()}.")
            return 0

        match request:
            case "register":
                result = self.__register_user(username, password) # Returns ID or -1 (exists)
                if result == -1:
                    return -2
                return result

            case "login":
                result = self.__login_user(username, password) # Returns ID or -1 (not found/wrong pass)
                if result == -1:
                    return -3
                return result

            case _:
                print(f"[Server] Invalid login request type '{request}' from {conn.getpeername()}.")
                return


    def __register_user(self, username, password) -> int:
        """ Registers a user. Returns user ID or -1 if username exists. """
        try:
            if self.__db_cursor.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone() is not None:
                return -1

            self.__db_cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.__db_conn.commit()
            user_id = self.__db_cursor.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
            return user_id[0] if user_id else -1
        except sql.Error as e:
            print(f"[Server] Database error during registration: {e}")
            self.__db_conn.rollback()
            return -1


    def __login_user(self, username, password) -> int:
        """ Logs in a user. Returns user ID or -1 if not found or wrong password. """
        try:
            user = self.__db_cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password)).fetchone()
            if user is None:
                return -1
            return user[0]
        except sql.Error as e:
            print(f"[Server] Database error during login: {e}")
            return -1


    def __cleanup_client(self, client_id: int):
        """ Safely cleans up resources associated with a disconnected client. """
        if client_id not in self.__connected_ids:
            return

        print(f"[Server] Cleaning up client ID {client_id}.")
        self.__connected_ids.remove(client_id)

        tcp_conn = self.__id_to_tcp_conn.pop(client_id, None)
        if tcp_conn:
            self.__tcp_conn_to_id.pop(tcp_conn, None)
            try:
                tcp_conn.shutdown(socket.SHUT_RDWR)
            except (OSError, socket.error): pass
            finally:
                try:
                    tcp_conn.close()
                except (OSError, socket.error): pass

        udp_addr = self.__id_to_udp_addr.pop(client_id, None)
        if udp_addr:
            self.__udp_addr_to_id.pop(udp_addr, None)

        if self.__on_disconnect:
            self.__on_disconnect(client_id)


    def stop(self):
        """ Stops the server network threads and closes sockets. """
        if not self._running:
            return
        print("[Server] Stopping network...")
        self._running = False

        if self.tcp_socket:
            try:
                self.tcp_socket.close()
                self.tcp_socket = None
            except socket.error: pass

        if self.udp_socket:
            try:
                self.udp_socket.close()
                self.udp_socket = None
            except socket.error: pass

        all_client_ids = list(self.__id_to_tcp_conn.keys())
        for client_id in all_client_ids:
            self.__cleanup_client(client_id)

        if self.__db_conn:
            self.__db_conn.close()
            self.__db_conn = None

        print("[Server] Network stopped.")

#?endif



