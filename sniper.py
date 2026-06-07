import asyncio
import aiohttp
import random
import string
import time
import os

class DiscordSniper:
    def __init__(self):
        self.token = os.environ.get('DISCORD_TOKEN')
        self.available_nicks = []
        self.checked_nicks = 0
        self.start_time = None
        self.rate_limit_delay = 2
        self.base_url = "https://discord.com/api/v9"

    def generate_nicks(self, pattern, length, count=5):
        chars = string.ascii_lowercase + string.digits
        nicks = []
        for _ in range(count):
            suffix = ''.join(random.choices(chars, k=length))
            nicks.append(f"{pattern}{suffix}")
        return nicks

    async def check_username(self, session, username):
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0',
        }
        url = f"{self.base_url}/unique-username/username-attempt-unauthed"
        
        try:
            async with session.post(url, json={"username": username}, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return not data.get('taken', True)
                elif resp.status == 429:
                    try:
                        retry = (await resp.json()).get('retry_after', 5)
                    except:
                        retry = 5
                    print(f"Rate limit! {retry}s bekleniyor...")
                    await asyncio.sleep(retry + 1)
                    return "retry"
                elif resp.status == 401:
                    print("Token gecersiz!")
                    return None
                else:
                    await asyncio.sleep(2)
                    return False
        except:
            await asyncio.sleep(3)
            return "retry"

    async def start_sniping(self, pattern, length):
        self.start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            print(f"BASLATILDI!")
            print(f"Pattern: {pattern} + {length} karakter")
            print(f"Gecikme: {self.rate_limit_delay}s")
            print("=" * 40)
            
            while True:
                nicks = self.generate_nicks(pattern, length, 5)
                
                for nick in nicks:
                    self.checked_nicks += 1
                    result = await self.check_username(session, nick)
                    
                    if result == True:
                        self.available_nicks.append(nick)
                        print(f"\n!!! MUSAIT NICK: {nick} !!!")
                    elif result is None:
                        print("Token hatasi! Durduruluyor...")
                        return
                    
                    print(f"Kontrol: {self.checked_nicks} - {nick}")
                    await asyncio.sleep(self.rate_limit_delay)
                
                if self.checked_nicks % 25 == 0:
                    elapsed = time.time() - self.start_time
                    print(f"\n[Durum] {elapsed:.0f}s | Kontrol: {self.checked_nicks} | Bulunan: {len(self.available_nicks)}\n")
                
                if self.checked_nicks % 50 == 0:
                    print("5 saniye mola...")
                    await asyncio.sleep(5)

async def main():
    sniper = DiscordSniper()
    
    if not sniper.token:
        print("HATA: DISCORD_TOKEN bulunamadi!")
        return
    
    pattern = os.environ.get('PATTERN', '4l')
    length = int(os.environ.get('LENGTH', '3'))
    delay = float(os.environ.get('DELAY', '2'))
    
    sniper.rate_limit_delay = delay
    await sniper.start_sniping(pattern, length)

if __name__ == "__main__":
    asyncio.run(main())