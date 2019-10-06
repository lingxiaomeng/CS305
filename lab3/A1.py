import asyncio


async def dispatch(reader, writer):
    while True:
        data = await reader.readline()
        print(data)
        if data and data != b'exit\r\n':  # 基于Ubuntu telnet测试
            writer.writelines([data])
            print(data)
        else:
            break
    await writer.drain()
    writer.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 7654, loop=loop)
    server = loop.run_until_complete(coro)
    print('Serving on{}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        exit()
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
