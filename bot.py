import re
import json
import asyncio
from urllib.parse import urljoin

import telepot
import telepot.async
import aiohttp


class ComposerBot(telepot.async.Bot):

    def __init__(self, *args, config=None, **kwargs):
        super(ComposerBot, self).__init__(*args, **kwargs)
        self.config = config
        self.mp3_regex = re.compile('<audio.*?<source src="(.*?)".*?<\/audio>', re.DOTALL)
        self.msg_regex = re.compile('<pre>.*?T: (.*?)\n.*?</pre>', re.DOTALL)

    async def send_result(self, chat_id, content):
        mp3_path = urljoin(self.config['base_url'], self.mp3_regex.findall(content)[0])
        pre_text = self.msg_regex.findall(content)[0]
        self.loop.create_task(self.sendChatAction(chat_id, 'upload_audio'))
        async with aiohttp.ClientSession(loop=self.loop) as client:
            async with client.get(mp3_path) as resp:
                await self.sendAudio(chat_id, await resp.content.read(), title=pre_text)

    async def status_poll(self, chat_id, location):
        url = urljoin(self.config['base_url'], location)
        print('start polling {}'.format(url))
        for _ in range(600):
            await asyncio.sleep(2)
            print('checking url {}'.format(url))
            async with aiohttp.ClientSession(loop=self.loop) as client:
                async with client.get(url) as resp:
                    content = await resp.text()
                    if content.find('<audio') != -1:
                        print("sending result {}".format(url))
                        self.loop.create_task(self.send_result(chat_id, content))
                        break
                    elif content.find('Composing...') != -1:
                        print("wait {}".format(url))
                    else:
                        print("error with url {}".format(url))
                        self.loop.create_task(self.sendMessage(chat_id, 'something went wrong with url {}'.format(url)))
                        break

    async def compose(self, chat_id):
        url = urljoin(self.config['base_url'], 'song/compose/')
        async with aiohttp.ClientSession(loop=self.loop) as client:
            async with client.get(url) as resp:
                if resp.status == 200:
                    location = resp.history[0].headers.get("Location")
                    self.loop.create_task(self.status_poll(chat_id, location))
                    self.loop.create_task(self.sendMessage(chat_id, '\U0001f40c please wait...'))

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(msg)
        if msg['text'].find('/compose') != -1:
            self.loop.create_task(self.compose(chat_id=chat_id))
        elif msg['text'].find('/start') != -1:
            self.loop.create_task(self.sendMessage(chat_id, "Hello! Please use /compose command!"))
        else:
            self.loop.create_task(self.sendMessage(chat_id, "I don't know what you mean. Try /compose command."))


with open('conf/config.json') as f:
    config = json.loads(f.read())

token = config.pop("telegram_token")
loop = asyncio.get_event_loop()
bot = ComposerBot(token=token, config=config, loop=loop)
loop.create_task(bot.message_loop())
print("listening...")

try:
    loop.run_forever()
finally:
    loop.close()
