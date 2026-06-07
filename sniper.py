import asyncio
import aiohttp
import random
import string
import time
import os

TOKEN = os.environ.get("TOKEN", "YOK")
WEBHOOK = os.environ.get("WEBHOOK", "YOK")

checked = 0
found = []

async def send_webhook(nick):
    if WEBHOOK == "YOK":
        return
    try:
        async with aiohttp.ClientSession() as s:
            await s.post(WEBHOOK, json={"content": f"MUSAIT NICK: {nick}"})
    except:
        pass

def gen():
    chars = string.ascii_lowercase + string.digits
    nicks = []
    for _ in range(5):
        l = random.randint(2, 5)
        nicks.append(''.join(random.choices(chars, k=l)))
    return nicks

async def check(session, nick):
    headers = {'Authorization': TOKEN, 'Content-Type': 'application/json'}
    url = "https://discord.com/api/v9/unique-username/username-attempt-unauthed"
    try:
        async with session.post(url, json={"username": nick}, headers=headers, timeout=10) as r:
            if r.status == 200:
                d = await r.json()
                return not d.get('taken', True)
            elif r.status == 429:
                await asyncio.sleep(5)
                return "retry"
    except:
        await asyncio.sleep(3)
    return False

async def main():
    global checked, found
    print("BASLATILDI!")
    
    async with aiohttp.ClientSession() as s:
        while True:
            for nick in gen():
                checked += 1
                result = await check(s, nick)
                if result == True:
                    found.append(nick)
                    print(f">>> MUSAIT: {nick} <<<")
                    await send_webhook(nick)
                print(f"[{checked}] {nick}")
                await asyncio.sleep(2)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print(f"\nDurduruldu!")