# import aiohttp
# import asyncio
# import time

# start_time = time.time()

# async def get_pokemon(session, number):
#     print("hi")
#     url = f'http://localhost:8000/test_endpoint/{number}'
#     print(f"request = {number} , {time.time()}")
#     async with session.get(url) as resp:
#         pokemon = await resp.json()
#         print(f"response = {pokemon['mes_id']} {time.time()}")
#         return pokemon

# async def main():
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for number in range(1, 10):
#             # print("hi")
#             # print(tasks)
#             tasks.append(get_pokemon(session, number))
#             await asyncio.sleep(1) 
#         original_pokemon = await asyncio.gather(*tasks)
#         # for pokemon in original_pokemon:
#         #     print(pokemon)

# asyncio.run(main())
# print("--- %s seconds ---" % (time.time() - start_time))


# ---------------------------------------------------------------------------
# import aiohttp
# import asyncio
# import time

# start_time = time.time()

# async def get_pokemon(session, number):
#     url = f'http://localhost:8000/test_endpoint/{number}'
#     print(f"request = {number} , {time.time()}")
#     async with session.get(url) as resp:
#         pokemon = await resp.json()
#         print(f"response = {number} {time.time()}")
#         return pokemon

# async def sleep_between_requests():
#     for _ in range(1, 151):
#         await asyncio.sleep(6)  # Introduce a 6-second interval between requests
#         print(f"Sleep completed at {time.time()}")

# async def main():
#     async with aiohttp.ClientSession() as session:
#         tasks = [get_pokemon(session, number) for number in range(1, 151)]
#         await asyncio.gather(*tasks, sleep_between_requests())

# asyncio.run(main())
# print("--- %s seconds ---" % (time.time() - start_time))


# ---------------------------------------------------------
import aiohttp
import asyncio
import time

start_time = time.time()

async def get_pokemon(session, number):
    url = f'http://localhost:8000/test_endpoint/{number}'
    print(f"request = {number} , {time.time()}")
    async with session.get(url) as resp:
        pokemon = await resp.json()
        print(f"response = {number} {time.time()}")
        return pokemon

async def main():
    async with aiohttp.ClientSession() as session:
        for number in range(1, 151):
            await get_pokemon(session, number)
            await asyncio.sleep(1)  # Introduce a 1-second interval between requests

asyncio.run(main())
print("--- %s seconds ---" % (time.time() - start_time))
