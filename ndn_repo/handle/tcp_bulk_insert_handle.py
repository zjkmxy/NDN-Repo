import asyncio as aio
import logging
import pickle
import sys
from . import ReadHandle, CommandHandle
from ..storage import *
from ndn.encoding import Name, read_tl_num_from_stream, parse_data
from ndn.encoding import TypeNumber


class TcpBulkInsertHandle(object):

    class TcpBulkInsertClient(object):
        """
        An instance of this nested class will be created for every new connection.
        """
        def __init__(self, reader, writer, storage: Storage, read_handle: ReadHandle):
            """
            TCP Bulk insertion client need to keep a reference to ReadHandle to register new prefixes.
            """
            self.reader = reader
            self.writer = writer
            self.storage = storage
            self.read_handle = read_handle
            self.m_inputBufferSize = 0
            logging.info("New connection")

        async def handleReceive(self):
            """
            Handle one incoming TCP connection.
            Multiple data packets may be transferred over a single connection.
            """
            while True:
                try:
                    ret = await read_tl_num_from_stream(self.reader)
                    assert ret == TypeNumber.DATA
                    siz = await read_tl_num_from_stream(self.reader)
                    data_bytes = await self.reader.readexactly(siz)
                except aio.IncompleteReadError as exc:
                    self.writer.close()
                    logging.info('Closed TCP connection')
                    return
                except Exception as exc:
                    print(exc)
                    return
                # Parse data again to obtain the name
                (data_name, _, _, _) = parse_data(data_bytes, with_tl=False)
                self.storage.put(Name.to_str(data_name), data_bytes)
                logging.info(f'Inserted data: {Name.to_str(data_name)}')
                # Register prefix for this data
                existing = CommandHandle.update_prefixes_in_storage(self.storage, data_name)
                if not existing:
                    self.read_handle.listen(data_name)

    def __init__(self, storage: Storage, read_handle: ReadHandle,
                 server_addr: str, server_port: str):
        """
        TCP bulk insertion handle need to keep a reference to ReadHandle to register new prefixes.
        """
        async def run():
            self.server = await aio.start_server(self.startReceive, server_addr, server_port)
            addr = self.server.sockets[0].getsockname()
            logging.info(f'Serving on {addr}')
            async with self.server:
                await self.server.serve_forever()

        self.storage = storage
        self.read_handle = read_handle
        event_loop = aio.get_event_loop()
        
        if sys.version_info.minor >= 7:
            # python 3.7+
            event_loop.create_task(run())
        else:
            coro = aio.start_server(self.startReceive, server_addr, server_port, loop=event_loop)
            server = event_loop.run_until_complete(coro)
            logging.info('Serving on {}'.format(server.sockets[0].getsockname()))

    async def startReceive(self, reader, writer):
        """
        Create a new client for every new connection.
        """
        logging.info("Accepted new TCP connection")
        client = TcpBulkInsertHandle.TcpBulkInsertClient(reader, writer, self.storage, self.read_handle)
        event_loop = aio.get_event_loop()
        event_loop.create_task(client.handleReceive())


if __name__ == "__main__":
    logging.basicConfig(format='[%(asctime)s]%(levelname)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    storage = LevelDBStorage()
    handle = TcpBulkInsertHandle(storage)

    event_loop = aio.get_event_loop()
    event_loop.run_forever()
