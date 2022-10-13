import asyncio
import base64

import aiohttp
from mirai import Mirai, WebSocketAdapter, GroupMessage, Image, Plain
from typing import List

from gen_bridge import predict, interrupt, img2img

bot = Mirai(
    qq=********,  # 改成你的机器人的 QQ 号
    adapter=WebSocketAdapter(
        verify_key='1145141919810', host='192.168.8.8', port=8080
    )
)
help = """text2img:
/ai prompts... [选项 [参数]]
    #opt 默认更二的negative prompt
    #neg 手动指定负面标签
    #step 20 采样次数
    #seed -1 种子
    #width 512 宽度
    #height 832 高度
    #cfg 7 CFG SCALE 
宽高可选:64,128,192,256,320,384,448,512,640,704,768,832,896,960,1024,1088,1152,1216,1280,1344,1408,1472,1536,1600,1664,1728,1792,1856,1920,1984,2048
关键词语法: {强调} [弱化] 混|合 及其:0.5|权重:-1
img2img:
/ai prompts... [选项] <图>
    #opt #neg #step 20 
    #height 512 #width 512 
    #cfg 7 #seed -1
    #sc RCF Resize Corp Fill 图像缩放模式
    #dn 0.5 越大噪声越大 [0,1]
"""


async def fetch_img(url: str):
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            img = response.content
            img_b64 = base64.b64encode(await img.read()).decode()
    img_type = 'jpeg' if img_b64[0] == '/' else 'png' if img_b64[0] == 'i' else 'null'
    return f'data:image/{img_type};base64,{img_b64}'


@bot.on(GroupMessage)
async def on_group_message(event: GroupMessage):
    msg = ' '.join(map(str, event.message_chain[Plain]))
    if msg == '/ai help':
        await bot.send(event, help)

    elif msg == '/ai #break':
        interrupt()

    elif msg.startswith('/ai'):
        if Image in event.message_chain:
            images: List[Image] = event.message_chain[Image]
            img_b64 = await fetch_img(url=images[0].url)

            args = msg.split(' ', maxsplit=1)[-1]
            args_list = args.split('#')
            prompt = args_list[0]
            option_args = {i[0]: i[1] if len(i) > 1 else True for i in
                           map(lambda x: x.split(' ', maxsplit=1), args_list[1:])}
            loop = asyncio.get_event_loop()
            result, seed = await loop.run_in_executor(None, lambda: img2img(img_b64, prompt, **option_args))
            await bot.send(event, [Image(base64=result), Plain(f'#seed {seed}')], quote=True)

        else:
            print(msg)

            with open("keyword.txt", 'a+') as rec:
                rec.writelines(f'{msg}\n')
                rec.flush()

            args = msg.split(' ', maxsplit=1)[-1]
            args_list = args.split('#')
            prompt = args_list[0]
            option_args = {i[0]: i[1] if len(i) > 1 else True for i in
                           map(lambda x: x.split(' ', maxsplit=1), args_list[1:])}
            loop = asyncio.get_event_loop()
            img_b64, seed = await loop.run_in_executor(None, lambda: predict(prompt, **option_args))
            await bot.send(event, [Image(base64=img_b64), Plain(f'#seed {seed}')], quote=True)


bot.run()
