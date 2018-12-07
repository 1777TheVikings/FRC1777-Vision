from typing import Any, NoReturn, List
from numpy import ndarray
import socket
import select
import xml.etree.ElementTree as ElementTree
import logging
import errno

from base_classes import PostProcessorBase


class SocketServerPostProcessor(PostProcessorBase):
    """
    Outputs data to clients as a TCP server.

    Configuration info:

    - `Port`: The port number of the TCP server. This must follow the port usage rules specified by the FRC Game
    Manual. A port number in the range 5800-5810 is recommended.
    """
    port = int()

    sock = None

    async def setup(self, component_config_root: ElementTree.Element):
        self.port = int(component_config_root.find("Port").text)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(5)
        logging.debug("Server listening on seaport " + str(self.port))
        
        self.read_list = [self.sock]
        self.write_list = []

    # noinspection PyMethodMayBeStatic
    async def cleanup(self):
        self.sock.close()

    async def postprocess(self, data: List[Any], frame: ndarray) -> NoReturn:
        def disconnect(s: socket.socket) -> NoReturn:
            if s in self.read_list:
                self.read_list.remove(s)
            if s in self.write_list:
                self.write_list.remove(s)
            if s in readable:
                readable.remove(s)
            if s in writable:
                writable.remove(s)
            s.close()
        
        try:
            readable, writable, errored = select.select(self.read_list, self.write_list, self.read_list, 0.02)
        except select.error as e:
            print(e)
        
        for s in errored:
            logging.warn("exceptional condition on " + str(s.getpeername()))
            disconnect(s)
        
        for s in readable:
            if s is self.sock:
                client_socket, address = self.sock.accept()
                logging.debug("Accepted connection from " + str(client_socket.getpeername()))
                client_socket.setblocking(0)
                self.read_list.append(client_socket)
                self.write_list.append(client_socket)
            else:
                data_in = s.recv(1024)
                if data_in:
                    if data_in.startswith(b"shutdown"):
                        raise KeyboardInterrupt
        
        for s in writable:
            if len(data) > 0:
                message = self.to_string(data[0])
                try:
                    s.send(bytes(message, "utf-8"))
                except socket.error as err:
                    if err.errno == errno.EPIPE:
                        logging.warn("client unexpectedly disconnected")
                        disconnect(s)
    
    @staticmethod
    def to_string(data: Any):
        return str(data.angle) + "\n"

