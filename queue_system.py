import asyncio

queue = asyncio.Queue()

async def worker():
    while True:
        func, args = await queue.get()
        try:
            await func(*args)
        except Exception as e:
            print("Worker Error:", e)
        queue.task_done()
