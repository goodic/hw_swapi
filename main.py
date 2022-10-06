import asyncio
import aiohttp
from more_itertools import chunked
from cache import AsyncLRU
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from migrate import People


URL = 'https://swapi.dev/api/people/'
PG_DSN = 'postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/swapi'
MAX = 100
PARTITION = 10
attr_list = ["gender", "hair_color", "name", "skin_color", "birth_year", "eye_color", "height", "mass"]
attr_list_url = ["species", "starships", "vehicles"]


engine = create_async_engine(PG_DSN)
Base = declarative_base(bind=engine)
DbSession = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def id_from_url(url: str):
    return url.split("/")[-2]


@AsyncLRU(maxsize=256)
async def get_some_name(session, some_url):
    async with session.get(some_url) as response:
        return await response.json()


async def get_names(session, urls):
    tasks = [asyncio.create_task(get_some_name(session, url)) for url in urls]
    for task in tasks:
        name = await task
        yield name


async def urls_to_names(session, urls, obj_keyname="name"):
    result_list = []
    async for name in get_names(session, urls):
        result_list.append(name[obj_keyname])
    return ','.join(result_list)


async def trim_person(session, person):
    task = asyncio.create_task(get_some_name(session, person["homeworld"]))
    name = await task
    result = {
        "id": int(id_from_url(person["url"])),
        "homeworld": name["name"]
    }
    for key in attr_list:
        result[key] = person[key]
    for key in attr_list_url:
        result[key] = await urls_to_names(session, person[key])
    result["films"] = await urls_to_names(session, person["films"], "title")
    return result


async def get_person(session, person_id):
    async with session.get(f'{URL}{person_id}') as response:
        return await response.json()


async def get_people(session, all_ids, partition):
    for chunk_ids in chunked(all_ids, partition):
        tasks = [asyncio.create_task(get_person(session, person_id)) for person_id in chunk_ids]
        for task in tasks:
            task_result = await task
            yield task_result


async def main():
    async with aiohttp.ClientSession() as http_session:
        async for people in get_people(http_session, range(1, MAX + 1), PARTITION):
            if "name" in people.keys():
                person = await trim_person(http_session, people)
                async with DbSession() as db_session:
                    db_session.add(People(**person))
                    await db_session.commit()


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
