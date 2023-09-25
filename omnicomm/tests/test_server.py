import random
import socket
import socketserver
import time
import unittest
from collections.abc import Generator
from contextlib import contextmanager
from queue import Queue
from threading import Thread

from omnicomm import commands
from omnicomm.protocol import RegistrarProtocol, ServerProtocol


class SimpleTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    request_queue_size = 1000
    daemon_threads = True


class SimpleTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        cmd80, remain = ServerProtocol.unpack(data)

        data = {'rec_id': random.randint(1, 100)}  # noqa: S311
        data = ServerProtocol.pack(commands.Cmd85(data))
        self.request.sendall(data)

        data = self.request.recv(1024)
        cmd86, remain = ServerProtocol.unpack(data)

        data = self.request.recv(1024)
        cmd86, remain = ServerProtocol.unpack(data)

        data = {'rec_id': random.randint(1, 100)}  # noqa: S311
        data = ServerProtocol.pack(commands.Cmd87(data))
        self.request.sendall(data)

        data = self.request.recv(1024)
        cmd88, remain = ServerProtocol.unpack(data)


Server = type[socketserver.ThreadingTCPServer]
ServerHandler = type[socketserver.BaseRequestHandler]


class Registrar(Thread):
    def __init__(self, host: str, port: int, q_input: Queue, q_output: Queue) -> None:
        self.host = host
        self.port = port
        self.q_input = q_input
        self.q_output = q_output

        super().__init__(daemon=True)

    def run(self):
        tasks = self.q_input.get()

        cmd = commands.Cmd80(dict(reg_id=0, firmware=tasks))
        data = RegistrarProtocol.pack(cmd)

        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client.connect((self.host, self.port))
        tcp_client.sendall(data)

        received = tcp_client.recv(1024)
        cmd85, remain = RegistrarProtocol.unpack(received)

        data = {
            'rec_id': 0,
            'omnicomm_time': 0,
            'priority': 0,
            'msgs': [
                {
                    'mID': [0x0B],
                    'general': {
                        'Time': 135433134,
                        'FLG': 7,
                        'Mileage': 0,
                        'VImp': 0,
                        'TImp': 1000,
                        'Uboard': 124,
                        'SumAcc': 102,
                    },
                    'nav': {
                        'LAT': 557887999,
                        'LON': 375883499,
                        'GPSVel': 3,
                        'GPSDir': 264,
                        'GPSNSat': 8,
                        'GPSAlt': 2096,
                    },
                },
            ],
        }
        cmd86 = commands.Cmd86(data)
        data = RegistrarProtocol.pack(cmd86)
        tcp_client.send(data)

        cmd86 = commands.Cmd86({})
        data = RegistrarProtocol.pack(cmd86)
        tcp_client.sendall(data)

        received = tcp_client.recv(1024)
        cmd87, remain = RegistrarProtocol.unpack(received)

        time.sleep(1)

        data = RegistrarProtocol.pack(commands.Cmd88(cmd87.value))
        tcp_client.sendall(data)

        time.sleep(0.1)

        self.q_output.put(1)

        self.q_input.task_done()


class TestServer(unittest.TestCase):
    @staticmethod
    @contextmanager
    def server(server_cls: Server, handler_cls: ServerHandler, host: str, port: int) -> Generator:
        server = server_cls((host, port), handler_cls)
        Thread(target=server.serve_forever, daemon=True).start()
        yield server
        server.server_close()

    def test_load(self):
        ServerProtocol.load_command_proto()

        q_input = Queue()
        q_output = Queue()

        host, port = 'localhost', 38700
        clients = 1
        messages = 1

        for _ in range(clients):
            q_input.put(messages)

        with self.server(SimpleTCPServer, SimpleTCPRequestHandler, host, port):
            for _ in range(clients):
                Registrar(host, port, q_input, q_output).start()

            q_input.join()

        self.assertTrue(len(list(filter(bool, q_output.queue))) == clients * messages)
