import sys, discord, requests, json, traceback, time, asyncio, os, pickle
import numpy as np
import pandas as pd
import datetime as dt
from pytz import timezone
from keys import token_str, steamapi_key_str, dev_id, id_bot_channel, modes, dotw
from search_videos import search_videos

global list_hero_name
f = open("./hero_name.txt","rb")
list_hero_name = pickle.load(f)

class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

    async def sendbotchannel(self, msg):
        '''bot用チャンネルに書き込む'''
        bot_channel = self.get_channel(id_bot_channel)
        await bot_channel.send(msg)

    async def send2developer(self, msg):
        '''開発者にDMを送る'''
        developer = self.get_user(dev_id)
        dm = await developer.create_dm()
        await dm.send(msg)

    async def send2user(self, user_id, msg):
        try:
            tmp_user = self.get_user(user_id)
            dm = await tmp_user.create_dm()
            await dm.send(msg)
        except Exception:
            await self.send2developer(traceback.format_exc())

    async def on_ready(self):
        msg = f'Logged on as {self.user}!'
        await self.send2developer(msg)

        dazzle_server = self.get_guild(456832624162373632)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def my_background_task(self):

        try:
            await self.wait_until_ready()
            while not self.is_closed():

                dt_now = dt.datetime.now(timezone('Asia/Tokyo'))

                if dt_now.minute == 10: # 毎時10分に発動
                    df_videos = search_videos()
                    df_members = pd.read_csv('members.csv')

                    for i in range(len(df_videos)):
                        row_tmp = df_videos.iloc[i,:]
                        hero_tmp = row_tmp['hero']
                        videoid_tmp = row_tmp['videoId']

                        target_user_list = list(df_members[df_members[hero_tmp] == True]['id'])

                        if target_user_list != []: 
                            m = ''

                            for target_id in target_user_list:
                                m+= '<@{}> '.format(target_id)

                            m += '\r\n' + hero_tmp + 'の新着動画があります\r\n'
                            m += 'https://www.youtube.com/watch?v=' + videoid_tmp

                            await self.sendbotchannel(m)

                await asyncio.sleep(60) # task runs every 60 seconds

        except Exception: # エラー発生時にはトレースバックがDMで送られてくる
            await self.send2developer(traceback.format_exc())



    async def on_message(self, message):
        """ メッセージ受信時のイベントハンドラ """
        try:
            if message.author.id == self.user.id:
                return

            if message.content.startswith("おはよう"):
                m = "おはようございます、" + message.author.name + "さん！"
                await message.channel.send(m)

            if message.content.startswith("おやすみ"):
                m = "おやすみなさい、" + message.author.name + "さん！"
                await message.channel.send(m)

            if message.content == '!help':
                m = 'まだ何もできません'
                await message.channel.send(m)

            if '無能' in message.content:
                m = '無能ちゃうわ！'
                await message.channel.send(m)

            if message.content.startswith('!bye'):
                '''終了用コマンド'''
                m = ':wave:'
                await message.channel.send(m)
                await self.close()

            if message.content.startswith('!addhero'):
                '''そのプレイヤー用のヒーローを登録'''
                search_word = message.content[8:].lstrip()
                found_list = [a for a in list_hero_name if search_word.lower() in a.lower()]

                if len(found_list) == 0:
                    m = 'ヒーローが見つかりませんでした'

                elif len(found_list) == 1:
                    target_hero_str = found_list[0]

                    df = pd.read_csv('members.csv')
                    df.loc[df['id'] == message.author.id, target_hero_str] = True
                    df.to_csv('members.csv',index=None)
                    m = found_list[0] + 'を登録しました'

                else:
                    m1 = str(len(found_list)) + '件のヒーローが見つかりました\r\n'
                    m2 = ''
                    for i in range(len(found_list)):
                        if i != len(found_list) - 1:
                            m2 += found_list[i] + ', '
                        else:
                            m2 += found_list[i] + '\r\n'
                    m3 = 'お手数ですが、!addheroからやり直してください'

                    m = m1+m2+m3

                await message.channel.send(m)


            if message.content.startswith('!delhero'):
                '''そのプレイヤー用のヒーローを削除'''
                search_word = message.content[8:].lstrip()
                found_list = [a for a in list_hero_name if search_word.lower() in a.lower()]

                if len(found_list) == 0:
                    m = 'ヒーローが見つかりませんでした'

                elif len(found_list) == 1:
                    target_hero_str = found_list[0]

                    df = pd.read_csv('members.csv')
                    df.loc[df['id'] == message.author.id, target_hero_str] = False
                    df.to_csv('members.csv',index=None)
                    m = found_list[0] + 'を削除しました'

                else:
                    m1 = str(len(found_list)) + '件のヒーローが見つかりました\r\n'
                    m2 = ''
                    for i in range(len(found_list)):
                        if i != len(found_list) - 1:
                            m2 += found_list[i] + ', '
                        else:
                            m2 += found_list[i] + '\r\n'
                    m3 = 'お手数ですが、!addheroからやり直してください'

                    m = m1+m2+m3

                await message.channel.send(m)

            if message.content.startswith('!check'):
                '''そのプレイヤーに登録されたヒーローを確認'''

                df = pd.read_csv('members.csv')
                target_row = df.loc[df['id'] == message.author.id, :]
                df_true = target_row[target_row == True]
                added_hero_list = list(df_true.columns[df_true[df_true==True].any()])

                if len(added_hero_list) == 0:
                    m = 'まだヒーローが登録されていません'

                else:
                    m1 = str(len(added_hero_list)) + '件のヒーローが登録されています\r\n'
                    m2 = ''
                    for i in range(len(added_hero_list)):
                        if i != len(added_hero_list) - 1:
                            m2 += added_hero_list[i] + ', '
                        else:
                            m2 += added_hero_list[i]

                    m = m1+m2

                await message.channel.send(m)

        except Exception: # エラー発生時にはトレースバックがDMで送られてくる
            await self.send2developer(traceback.format_exc())

client = MyClient()
client.run(token_str)