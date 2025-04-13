import requests
from aiogram.types import ContentType
import pytz
import datetime
import aiohttp
import asyncio
import logging
import sys
from aiogram.types import ChatPermissions
from aiogram.fsm.state import State, StatesGroup
from os import getenv
from aiogram import Bot, Dispatcher, html, types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.types import ContentType
from aiogram.filters import Command, StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import Button
from aiogram.types import InputMediaAudio
from bd import check_user, set_user, check_limity, zamena_limitov, set_time, check_time, get_all_users_point, dell_time_user, get_role, set_role, dell_role, spisok_admin, set_time_mute, check_time_mute, dell_time_user_mute, get_all_users_mute, set_text_mute, check_text_mute, dell_text_user_mute, check_warn_text, set_warn, check_warn, dell_user_bd, unwarn_users

router = Router()

tg_bot_token = '7739725001:AAEbC4KV8Hh09K90JSkKfvaLLGejGI86D4w'
bot = Bot(token=tg_bot_token)
dp = Dispatcher()

COMMAND_PREFIX = '-'
beseda = -1002383045817
ADMIN_ID = 1334301235

message_id = None
chat_id = None
user_id = None
user_id_unwarn = None
message_id_unwarn = None
chat_id_unwarn = None

my_router = Router(name=__name__)

class Form(StatesGroup):
    waiting_for_audio = State()
    
@dp.message(Command('start'))
async def start(message: types.Message):
    chat_type = message.chat.type
    global message_id, chat_id, user_id
    user_id = message.from_user.id
    chat_id = message.chat.id
    try:
        if chat_type == 'private':
            user = await check_user(user_id)
            member = await bot.get_chat_member(beseda, message.from_user.id)
            if member.status in ['member', 'administrator', 'creator']:
                if user == None:
                    name = message.from_user.first_name
                    fname = message.from_user.last_name
                    first_name = f'{name} {fname}'
                    user = message.from_user.username
                    username = f'@{user}'
                    await set_user(user_id, chat_id, first_name, username)
            
            
                    sent_message = await message.answer(text=f'Тебя приветствует бот диджея \n '
                                                        'Ashen Dj\n'
                                                        'Выбери нужную кнопку снизу:', reply_markup=Button.Knopki)
                    message_id = sent_message.message_id
                    chat_id = message.chat.id
                else:
                    sent_message = await message.answer(text=f'Старт-меню:\n'
                                                        'Выбери нужную кнопку снизу:', reply_markup=Button.Knopki)
                    message_id = sent_message.message_id
                    chat_id = message.chat.id
            else:
                await bot.send_message(chat_id=chat_id, text=f'Чтобы пользоваться ботом, нужно состоять в группе', reply_markup=Button.tg_gryppa)
                return
        else:
            await bot.send_message(chat_id=chat_id, text=f'Эта комманда предназначена для личных сообщений со мной!')
            return
    
    except Exception as e:
        await message.answer(f"Ошибка при проверке: {e}")
    
async def check_and_update_users():
    users = await get_all_users_point()
    current_time = datetime.datetime.now()

    for user in users:
        user_id = user['user_id']
        limity = user['limity']
        last_update = user['last_update']
        if last_update != None:
            if limity == 0:
                time_diff = last_update - current_time
                time_send_chas = int(time_diff.total_seconds() / 3600)
                time_send_min = int((time_diff.total_seconds() % 3600) // 60)
                if time_send_chas == 0 and time_send_min < 1 or time_send_chas < 0:
                    new_limity = 3
                    await zamena_limitov(new_limity, user_id)
                    print(user_id)
                    await dell_time_user(user_id)
                    print(f"Для пользователя {user_id} обновлены лимиты.")
                    await bot.send_message(chat_id=user_id, text="Ваши лимиты обновлены, можете отправлять песни снова!")
                    
async def check_and_update_users_mute():
    users = await get_all_users_mute()
    current_time = datetime.datetime.now()

    for user in users:
        user_name_bd = user['username']
        f_name = user['first_name']
        last_update = user['mut_time']
        user_id = user['user_id']
        if last_update != None:
            user_name = user_name_bd.lstrip('@')
            time_diff = last_update - current_time
            time_send_chas = int(time_diff.total_seconds() / 3600)
            time_send_min = int((time_diff.total_seconds() % 3600) // 60)
            time_send_sec = int(time_diff.total_seconds() % 60)
            if time_send_chas == 0 and time_send_min < 1 and time_send_sec < 4 or time_send_chas < 0:
                permissions = ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_audios=True,
                    can_send_documents=True,
                    can_send_video=True,
                    can_send_voice=True,
                    can_send_video_notes=True,
                    )
                await dell_time_user_mute(user_id)
                await bot.restrict_chat_member(chat_id=beseda,user_id=user_id, permissions=permissions)
                await dell_text_user_mute(user_id)
                await bot.send_message(chat_id=beseda, text=f"С пользователя [{f_name}](https://t.me/{user_name}) был снят мут!\n"
                                       f"Причина:\n"
                                       f"Срок действия окончен.", parse_mode="Markdown")
                   
                                  
async def periodic_check():
    while True:
        await check_and_update_users()
        await check_and_update_users_mute()
        await asyncio.sleep(3)
        

@dp.message(StateFilter(Form.waiting_for_audio), F.audio)
async def process_mp3(message: types.Message, state: FSMContext):
    current_time = datetime.datetime.now()
    user_id = message.from_user.id
    koll_point = await check_limity(user_id)
    print(koll_point)
    audio = message.audio
    if koll_point != 0:
        if audio.mime_type == 'audio/mpeg':
            id_chat_groop = 8
            koll_point -= 1
            user = await check_user(user_id)
            print(user)
            if koll_point == 0:
                
                time_plus_24h = current_time + datetime.timedelta(hours=24)
                await set_time(time_plus_24h, user_id)
                await message.answer(f"Спасибо за отправку музыки! 🎶\n"
                                     f"У вас закончились попытки,\n"
                                     f"возвращайтесь завтра.")
                name = message.from_user.first_name
                fname = message.from_user.last_name
                first_name = f'{name} {fname}'
                user = message.from_user.username
                new_caption = f'Отправил пользователь:\n<blockquote>Имя: {first_name}\nЮз: @{user}\nСсылка: https://t.me/{user}\nСтатус трека: 🕐Ожидание проверки</blockquote>\n'
                await bot.send_audio(chat_id=beseda, audio=audio.file_id,caption=new_caption, parse_mode='HTML', message_thread_id=id_chat_groop, reply_markup=Button.yes_no)
                await zamena_limitov(koll_point, user_id)
                await state.clear()
                                     
            else:
                await message.answer(f"Спасибо за отправку музыки! 🎶\n"
                                     f"У вас осталось: {koll_point} попыток!\n"
                                     f"Если хотите отправить еще один трек, пропишите заново\n"
                                     f"/smusic")
                name = message.from_user.first_name
                fname = message.from_user.last_name
                first_name = f'{name} {fname}'
                user = message.from_user.username
                new_caption = f'Отправил пользователь:\n<blockquote>Имя: {first_name}\nЮз: @{user}\nСсылка: https://t.me/{user}\nСтатус трека: 🕐Ожидание проверки</blockquote>\n'
                await bot.send_audio(chat_id=beseda, audio=audio.file_id,caption=new_caption, parse_mode='HTML', message_thread_id=id_chat_groop, reply_markup=Button.yes_no)
                await state.clear()
                await zamena_limitov(koll_point, user_id)
            
    else:
        time_bd = await check_time(user_id)
        if time_bd:
            time_edit = time_bd - current_time
            time_send_chas = int(time_edit.total_seconds() / 3600)
            time_send_min = int((time_edit.total_seconds() % 3600) // 60)
            await message.answer(f"У вас закончились попытки!\n"
                                 f"Следующее пополнение через:\n"
                                 f"<blockquote>{time_send_chas} часа(ов) {time_send_min} минут(ы)!</blockquote> ", parse_mode='HTML')
            
            
        
        
"""
@dp.message(F.text)
async def handle_message(message: types.Message):
    if not isinstance(message, types.Message):
        print("Ошибка: получен не тип Message.")
    
    if hasattr(message, 'chat'):
        chat_type = message.chat.type
        if chat_type != 'private':
            if hasattr(message, 'message_id'):
                message_id = message.message_id
                user_name_chat = message.from_user.username
                user_id = message.from_user.id

                chek_user = await check_user(user_id)
                if chek_user:
                    username = chek_user.get('username')

                    if username != user_name_chat:
                        await update_username(user_name_chat, user_id)
"""

@dp.message(Command('рег'))
async def start(message: types.Message):
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    name = message.reply_to_message.from_user.first_name
    fname = message.reply_to_message.from_user.last_name
    first_name = f'{name} {fname}'
    user = message.reply_to_message.from_user.username
    username = f'@{user}'
    await set_user(user_id, chat_id, first_name, username)
    await bot.send_message(chat_id=chat_id, text=f'Пользователь {first_name} зарегистрирован!')
        
@dp.callback_query(lambda c: c.data in ['info', 'top', 'help', 'send_music', 'menu', 'yes', 'no'])
async def handle_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    print(data)
    print(callback_query.from_user.id)
    
    await bot.answer_callback_query(callback_query.id)
        
    if data == 'info':
        message_id = callback_query.message.message_id
        chat_id = callback_query.message.chat.id
        await bot.edit_message_text(
        text=f'Вы нажали кнопку: {data}', reply_markup=Button.menu_but,
        chat_id=chat_id,
        message_id=message_id)
            
    if data == 'top':
        message_id = callback_query.message.message_id
        chat_id = callback_query.message.chat.id
        await bot.edit_message_text(
        text=f'Вы нажали кнопку: {data}', reply_markup=Button.menu_but,
        chat_id=chat_id,
        message_id=message_id)
            
    if data == 'help':
        message_id = callback_query.message.message_id
        chat_id = callback_query.message.chat.id
        await bot.edit_message_text(
        text=f'Вы нажали кнопку: {data}', reply_markup=Button.menu_but,
        chat_id=chat_id,
        message_id=message_id)
            
    if data == 'send_music':
        message_id = callback_query.message.message_id
        chat_id = callback_query.message.chat.id
        await bot.edit_message_text(
        text=f'Чтобы отправить свои песни на прослушивание администрации,\n'
        'нужно прописать команду: \n'
        '<blockquote>🔹                   /smusic                      🔹</blockquote>', parse_mode='HTML', reply_markup=Button.menu_but,
        chat_id=chat_id,
        message_id=message_id)
                
    if data == 'menu':
        message_id = callback_query.message.message_id
        chat_id = callback_query.message.chat.id
        await bot.edit_message_text(
        text=f'Выбери нужную кнопку снизу:', reply_markup=Button.Knopki,
        chat_id=chat_id,
        message_id=message_id)
            
    if data == 'yes':
        message_id = callback_query.message.message_id
        chat_id = callback_query.message.chat.id
        current_audio_file_id = callback_query.message.audio.file_id
        if callback_query.from_user.id == ADMIN_ID:
            new_caption = "\n\nСтатус трека: ✅Одобрено!"

            await bot.edit_message_media(
            InputMediaAudio(media=current_audio_file_id, caption=new_caption),
            chat_id=chat_id,
            message_id=message_id)
        else:
            chat_id_user = callback_query.from_user.id
            await bot.send_message(chat_id=chat_id_user, text="Кнопки действуют только на Администраторов!")
                

        
    if data == 'no':
        message_id = callback_query.message.message_id
        chat_id = callback_query.message.chat.id
        current_audio_file_id = callback_query.message.audio.file_id
        if callback_query.from_user.id == ADMIN_ID:
            new_caption = "\n\nСтатус трека: ❌Отказано!"

            await bot.edit_message_media(
            InputMediaAudio(media=current_audio_file_id, caption=new_caption),
            chat_id=chat_id,
            message_id=message_id)
        else:
            chat_id_user = callback_query.from_user.id
            await bot.send_message(chat_id=chat_id_user, text="Кнопки действуют только на Администраторов!")
                 
        
        
@dp.message(Command('smusic'))
async def smusic(message: types.Message, state: FSMContext):
    chat_type = message.chat.type
    
    try:
        global message_id, chat_id, user_id
        user_id = message.from_user.id
        chat_id = message.chat.id
        user = await check_user(user_id)
        print(f'User:{user}')
        member = await bot.get_chat_member(beseda, message.from_user.id)
        if member.status in ['member', 'administrator', 'creator']:
            if chat_type == 'private':
                time = await check_time(user_id)
                point = await check_limity(user_id)
                print(point)
                if user != None:
                    if point != 0:
                        await message.answer("Отправьте песни в MP3 формате.\n"
                                             "(Внимание): Песни отправлять лучше по одной!")
                
                        await state.set_state(Form.waiting_for_audio)
                    else:
                        if time:
                            current_time = datetime.datetime.now()
                            time_edit = time - current_time
                            time_send_chas = int(time_edit.total_seconds() / 3600)
                            time_send_min = int((time_edit.total_seconds() % 3600) // 60)
                            await message.answer(f"У вас закончились попытки!\n"
                                                 f"Следующее пополнение через:\n"
                                                 f"<blockquote>{time_send_chas} часа(ов) {time_send_min} минут(ы)!</blockquote> ", parse_mode='HTML')
                        else:
                            print( " NONE")
                else:
                    await message.answer("Не могу найти вас в базе данных!\n"
                                   "Пропишите команду:\n"
                                   "<blockquote>🔹                     /start                        🔹</blockquote>", parse_mode='HTML')
                        
            else:
                await bot.send_message(chat_id=chat_id, text=f'Эта команда предназначена для личных сообщений со мной!')
                
        else:
            await bot.send_message(chat_id=chat_id, text=f'Чтобы пользоваться ботом, нужно состоять в группе', reply_markup=Button.tg_gryppa)
    
    except Exception as e:
        await message.answer(f"Ошибка при проверке: {e}")            

@dp.message(Command('мойюз'))
async def username(message: types.Message):
    chat_id = message.chat.id
    print(chat_id)
    user =  message.from_user.username   
    await message.reply(f'Твой юз: @{user}')
    

@dp.message(Command('назначить'))
async def set_roli_beseda(message: types.Message):
    global message_id, user_id
    user_id = message.from_user.id
    chat_type = message.chat.type
    chat_id = message.chat.id
    
    try:
    
        if chat_type != 'private':
            if user_id == ADMIN_ID:
                if message.reply_to_message:
                    user_id_reply =  message.reply_to_message.from_user.id
                    roli_bd = await get_role(user_id_reply)
                    if roli_bd:
                        for role in roli_bd:
                            rol = role['user_role']
                            if rol == 'tex':
                                rol = 'Технический специалист'
                        
                            if rol == 'admin':
                                rol = 'Администратор'
                        
                            if rol == 'moder':
                                rol = 'Модератор'
                        
                            if rol == 'moder_stazh':
                                rol = 'Модер Стажёр'
                    else:
                        rol = None
                            
                    if rol == None:
                        sent_message = await bot.send_message(chat_id=chat_id, text=f'Выберите роль для пользователя:', reply_markup=Button.roli)
                        user_id = user_id_reply
                        message_id = sent_message.message_id
                    else:
                        user_id = user_id_reply
                        await message.answer(f"Пользователь уже имеет роль: {rol}", reply_markup=Button.dell_rol_button)
                else:
                    await message.answer("Вы должны ответить на сообщение пользователя!(Переделать под юз)")
            else:
                await message.answer("Назначать администраторов может только Создатель беседы!")
    
        else:
            await message.answer("Данная команда не доступна в личных сообщениях с ботом.")
            
    except Exception as e:
        await message.answer(f"Ошибка при проверке: {e}")
        
@dp.callback_query(lambda c: c.data in ['tex', 'admin', 'moder', 'moder_stazh', 'dell_rol'])
async def knopki_admin(callback_query: types.CallbackQuery):
    data = callback_query.data
    global user_id
    
    await bot.answer_callback_query(callback_query.id)
    
    if data == 'tex':
        if callback_query.from_user.id == ADMIN_ID:
            message_id = callback_query.message.message_id
            chat_id = callback_query.message.chat.id
            rol_tex = 'tex'
            await set_role(rol_tex, user_id)
            await bot.edit_message_text(text='Пользователь назначен на роль:\n'
                                        '<blockquote>Технический специальст</blockquote>', parse_mode='HTML', message_id=message_id, chat_id=chat_id)
            
        else:
            chat_id_user = callback_query.from_user.id
            await bot.send_message(chat_id=chat_id_user, text="Кнопки действуют только на Создателя чата!")
            
    if data == 'admin':
        if callback_query.from_user.id == ADMIN_ID:
            message_id = callback_query.message.message_id
            chat_id = callback_query.message.chat.id
            rol_admin = 'admin'
            await set_role(rol_admin, user_id)
            await bot.edit_message_text(text='Пользователь назначен на роль:\n'
                                        '<blockquote>Администратор</blockquote>', parse_mode='HTML', message_id=message_id, chat_id=chat_id)
            
        else:
            chat_id_user = callback_query.from_user.id
            await bot.send_message(chat_id=chat_id_user, text="Кнопки действуют только на Создателя чата!")
            
    if data == 'moder':
        if callback_query.from_user.id == ADMIN_ID:
            message_id = callback_query.message.message_id
            chat_id = callback_query.message.chat.id
            rol_moder = 'moder'
            await set_role(rol_moder, user_id)
            await bot.edit_message_text(text='Пользователь назначен на роль:\n'
                                        '<blockquote>Модератор</blockquote>', parse_mode='HTML', message_id=message_id, chat_id=chat_id)
            
        else:
            chat_id_user = callback_query.from_user.id
            await bot.send_message(chat_id=chat_id_user, text="Кнопки действуют только на Создателя чата!")
            
    if data == 'moder_stazh':
        if callback_query.from_user.id == ADMIN_ID:
            message_id = callback_query.message.message_id
            chat_id = callback_query.message.chat.id
            rol_moder_stazh = 'moder_stazh'
            await set_role(rol_moder_stazh, user_id)
            await bot.edit_message_text(text='Пользователь назначен на роль:\n'
                                        '<blockquote>Модер Стажёр</blockquote>', parse_mode='HTML', message_id=message_id, chat_id=chat_id)
            
        else:
            chat_id_user = callback_query.from_user.id
            await bot.send_message(chat_id=chat_id_user, text="Кнопки действуют только на Создателя чата!")
        
    if data == 'dell_rol':
        if callback_query.from_user.id == ADMIN_ID:
            message_id = callback_query.message.message_id
            chat_id = callback_query.message.chat.id
            await dell_role(user_id)
            await bot.edit_message_text(text='Роль с пользователя снята.' ,message_id=message_id, chat_id=chat_id)
            
        else:
            chat_id_user = callback_query.from_user.id
            await bot.send_message(chat_id=chat_id_user, text="Кнопки действуют только на Создателя чата!")
            
    
@dp.message(Command('админы'))
async def set_roli_beseda(message: types.Message):
    chat_type = message.chat.type
    
    try:
        
        if chat_type != 'private':
            chat_id = message.chat.id
            chat_members = await bot.get_chat_administrators(chat_id)
            for member in chat_members:
                if member.status == 'creator':
                    user_name_creator = member.user.username
                    first_name_creator = f'{member.user.first_name} {member.user.last_name}'
                
            tex, admin, moder, moder_stazh  =  await spisok_admin()
    
    
            if user_name_creator and first_name_creator:
                creator = f'🔥Создатель чата:\n ❗️[{first_name_creator}](https://t.me/{user_name_creator}) \n'
            else:
                creator =f'🔥Создатель чата:\n'
                f'Не найден.'

            if tex is None or admin is None or moder is None or moder_stazh is None:
                await message.answer("Ошибка при получении данных из базы данных.")
                return

            if tex:
                tex_list = "🔆Технические специалисты:\n"
                for i, texi in enumerate(tex, start=1):
                    username_bd = texi['username']
                    username = username_bd.lstrip('@')
                    first_name = texi['first_name']
                    tex_list += f"❗️{i}.[{first_name}](https://t.me/{username})\n"
            else:
                tex_list = "⛔️Технические специалисты отсутствуют!\n"

            if admin:
                admin_list = "🔆Администраторы:\n"
                for i, admini in enumerate(admin, start=1):
                    username_bd = admini['username']
                    username = username_bd.lstrip('@')
                    first_name = admini['first_name']
                    admin_list += f"❗️{i}.[{first_name}](https://t.me/{username})\n"
            else:
                admin_list = "⛔️Администраторы отсутствуют!\n"
        
            if moder:
                moder_list = "🔆Модераторы:\n"
                for i, moderi in enumerate(moder, start=1):
                    username_bd = moderi['username']
                    username = username_bd.lstrip('@')
                    first_name = moderi['first_name']
                    moder_list += f"❗️{i}.[{first_name}](https://t.me/{username})\n"
            else:
                moder_list = "⛔️Модераторы отсутствуют!\n"
        
            if moder_stazh:
                moder_stazh_list = "🔆Модераторы Стажёры:\n"
                for i, moderi_stazhori in enumerate(moder_stazh, start=1):
                    username_bd = moderi_stazhori['username']
                    username = username_bd.lstrip('@')
                    first_name = moderi_stazhori['first_name']
                    moder_stazh_list += f"❗️{i}.[{first_name}](https://t.me/{username})\n"
            else:
                moder_stazh_list = "⛔️Модераторы Стажёры отсутствуют!\n"

            await bot.send_message(chat_id=chat_id, text=f'{creator} \n' f'{tex_list} \n  {admin_list} \n {moder_list} \n {moder_stazh_list}', parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await message.answer("Данная команда доступна только в беседе!")
            
    except Exception as e:
        await message.answer(f"Ошибка при проверке: {e}")


  
@dp.message(Command('мут'))
async def set_roli_beseda(message: types.Message):
    bot_id_1 = await message.bot.get_me()
    bot_id_2 = bot_id_1.id
    chat_type = message.chat.type
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_status_0 = await bot.get_chat_member(chat_id, message.from_user.id)
    user_status = user_status_0.status
    current_time = datetime.datetime.now()
    
    try:

        if chat_type != 'private':
            status_bd = await get_role(user_id)
            if status_bd:
                for stat in status_bd:
                    status_1 = stat['user_role']
                status = status_1
                if status in ['tex', 'admin', 'moder', 'moder_stazh'] or user_status == 'creator':
                    if message.reply_to_message:
                        user_id_reply_message = message.reply_to_message.from_user.id
                        status_reply_message_bd = await get_role(user_id_reply_message)
                        print(status_reply_message_bd)
                        if user_id_reply_message != bot_id_2:
                            if status_reply_message_bd:
                                for stat_rep in status_reply_message_bd:
                                    status_reply_message_1 = stat_rep['user_role']
                                status_reply_message = status_reply_message_1
                    
                                user_status_reply_message_0 = await bot.get_chat_member(chat_id, message.reply_to_message.from_user.id)
                                user_status_reply_message = user_status_reply_message_0.status
                                check_time = await check_time_mute(user_id_reply_message)
                                if status_reply_message not in ['tex', 'admin', 'moder', 'moder_stazh'] and user_status_reply_message != 'creator':
                                    if check_time is None:
                                        if len(message.text.split()) == 4:
                                            time = await check_text(message.text)
                                            try:
                                                mute_minutes = int(message.text.split()[1])
                                            except ValueError:
                                                await message.answer("Введите корректное кол-во минут!\n"
                                                                     "Пример:\n"
                                                                     "<blockquote>🔹     /мут 30 минут       🔹</blockquote>")
                                                return
                                        else:
                                            await message.answer("Вы не правильно ввели команду:\n"
                                                                 "Пример:\n"
                                                                 "<blockquote>🔹  /мут 1 минута (причина)   🔹</blockquote>", parse_mode='HTML')
                                            return
                        
                                        await set_time_mute(time, user_id_reply_message)
                                        text = message.text.split()[3]
                                        await set_text_mute(text, user_id_reply_message)
                                        user_name = message.reply_to_message.from_user.username
                                        name = message.reply_to_message.from_user.first_name
                                        fname = message.reply_to_message.from_user.last_name
                                        first_name = f'{name} {fname}'
                        
                                        permissions = ChatPermissions(
                                            can_send_messages=False,
                                            can_send_media_messages=False,
                                            can_send_audios=False,
                                            can_send_documents=False,
                                            can_send_video=False,
                                            can_send_voice=False,
                                            can_send_video_notes=False,
                                            )
 

                                        time_edit = time - current_time
                                        time_send_day, time_send_chas, time_send_min = convert_time(time_edit)

                                        await bot.send_message(chat_id=chat_id, text=f"Пользователь [{first_name}](https://t.me/{user_name}) замучен на {time_send_day} дней {time_send_chas} час(ов) {time_send_min} минут(ы)\n"
                                                               f"Причина:\n"
                                                               f"{message.text.split()[3]}", parse_mode="Markdown", disable_web_page_preview=True)
                                        await bot.restrict_chat_member(chat_id=chat_id,user_id=user_id_reply_message, permissions=permissions)
                        
                                    else:
                                        time_edit = check_time - current_time
                                        time_send_day, time_send_chas, time_send_min = convert_time(time_edit)
                                        prichina = await check_text_mute(user_id_reply_message)

                                        await bot.send_message(chat_id=chat_id, text=f'Пользователь уже имеет мут!\n'
                                                               f'Причина:\n'
                                                               f'{prichina}\n'
                                                               f'До конца окончания мута:\n'
                                                               f'<blockquote>{time_send_day} дней {time_send_chas} час(а) {time_send_min} минут(а) </blockquote>', parse_mode='HTML')
                                        return
                        
                                else:
                                    await message.answer("Запрещено мутить пользователя, имеющий роль модератора и выше!")
                                    return
                        
                            else:
                                await message.answer("Не могу найти пользователя в базе данных!\n"
                                                     "Кикните его, и попросите чтобы заново написал боту в личные сообщения.")
                    
                        else:
                            await message.answer("Вы не можете меня замутить.")
                    
                    else:
                        await message.answer("Вы должны ответить командой на сообщение пользователя!")
                        return
            
                else:
                    await message.answer("Данная команда доступна только администраторам чата!")
                    return
        
            else:
                await message.answer("Вы не можете пользоваться командой, т.к вас нету в базе данных.")   
        
        else:
            await message.answer("Данная команда не доступна в личном чате со мной.")
            return
        
    except Exception as e:
        await message.answer(f"Ошибка при проверке: {e}")
    

async def check_text(text):
    current_time = datetime.datetime.now()
    if len(text.split()) < 3:
        raise ValueError("Неверный формат! Пример: '/мут 30 минут (причина)'")

    znachenie = text.split()[2].lower()
    time = int(text.split()[1])

    if znachenie in ["часов", "час", "часа"]:
        time_plus = current_time + datetime.timedelta(hours=time)
        return time_plus
    
    if znachenie in ["дней", "день", "дня"]:
        time_plus = current_time + datetime.timedelta(days=time)
        return time_plus
    
    if znachenie in ["минута", "минуты", "минут"]:
        time_plus = current_time + datetime.timedelta(minutes=time)
        return time_plus
    
    raise ValueError(f"Неизвестная единица времени: {znachenie}")

def convert_time(time_delta):
    time_send_day = int(time_delta.total_seconds() / 86400)
    time_send_chas = int((time_delta.total_seconds() % 86400) / 3600)
    time_send_min = int((time_delta.total_seconds() % 3600) // 60)
    return time_send_day, time_send_chas, time_send_min

@dp.message(Command('размут'))
async def set_roli_beseda(message: types.Message):
    try:
        
        chat_id = message.chat.id
        bot_id_1 = await message.bot.get_me()
        bot_id_2 = bot_id_1.id
        user_id = message.from_user.id
        chat_type = message.chat.type
        user_status_0 = await bot.get_chat_member(chat_id, message.from_user.id)
        user_status = user_status_0.status
    
        if chat_type != 'private':
            status_bd = await get_role(user_id)
            if status_bd:
                for stat in status_bd:
                    status_1 = stat['user_role']
                status = status_1
                if status in ['tex', 'admin', 'moder', 'moder_stazh'] or user_status == 'creator':
                    if message.reply_to_message:
                        user_id_reply_message = message.reply_to_message.from_user.id
                        status_reply_message_bd = await get_role(user_id_reply_message)
                        print(status_reply_message_bd)
                        if user_id_reply_message != bot_id_2:
                            if user_id != user_id_reply_message:
                                if status_reply_message_bd:
                                    for stat_rep in status_reply_message_bd:
                                        status_reply_message_1 = stat_rep['user_role']
                                    status_reply_message = status_reply_message_1
                                
                                    user_status_reply_message_0 = await bot.get_chat_member(chat_id, message.reply_to_message.from_user.id)
                                    user_status_reply_message = user_status_reply_message_0.status
                                    check_time = await check_time_mute(user_id_reply_message)
                                    if status_reply_message not in ['tex', 'admin', 'moder', 'moder_stazh'] and user_status_reply_message != 'creator':
                                        if check_time != None:
                                            if len(message.text.split()) == 2:
                                                
                                                permissions = ChatPermissions(
                                                    can_send_messages=True,
                                                    can_send_media_messages=True,
                                                    can_send_audios=True,
                                                    can_send_documents=True,
                                                    can_send_video=True,
                                                    can_send_voice=True,
                                                    can_send_video_notes=True,
                                                    )
                                                user_name = message.from_user.username
                                                await dell_time_user_mute(user_id_reply_message)
                                                await bot.restrict_chat_member(chat_id=beseda,user_id=user_id_reply_message, permissions=permissions)
                                                await dell_text_user_mute(user_id_reply_message)
                                                await message.answer('Мут снят\n'
                                                                     f'Причина:\n'
                                                                     f'{message.text.split()[1]}\n'
                                                                     f'Снял: [{"Администратор"}](https://t.me/{user_name})', parse_mode="Markdown", disable_web_page_preview=True)
                                            
                                            else:
                                                await message.answer("Укажите причину снятия мута.")
                                                return
                                        else:
                                            await message.answer('Пользователь не имеет мута.')
                                
                                    else:
                                        message.answer("У администраторов не может быть мута:)")
                                        return
                                else:
                                    await message.answer("Ошибка бд")
                                    return
                            else:
                                await message.answer("Вы не можете снять мут самому себе.")
                                return
                        else:
                            await message.answer("Я не могу иметь мута:)")
                            return
                    else:
                        await message.answer("Вы должны ответить командой на сообщение пользователя.")
                        return
                else:
                    await message.answer("Команда доступна только модераторам и выше.")
                    return
            else:
                await message.answer("Не могу найти вашу роль, обратитесь к Тех.специалисту или создателю чата.")
                return
        else:
            await message.answer("Данная команда не доступна в личном чате со мной.")
            return
        
    except Exception as e:
        await message.answer(f"Ошибка при проверке: {e}")
     
async def avto_message_warning(text, id, id_reply,time_vid, text_prich):
    chat_id = -1002412151822
    try:
        if text == 'WARN':
            coint_id = await check_warn(id_reply)
            if coint_id == 1:
                chek = await check_user(id_reply)
                username = chek['username']
                
                chek_adm = await check_user(id)
                username_adm = chek_adm['username']
                
                await bot.send_message(chat_id=chat_id, text=f"🚨Выдан варн (1/3)\n"
                                       f"  <blockquote>🌵Пользователю: {username}\n"
                                       f"  👤Администратором: {username_adm}\n"
                                       f"  🛑Причина: <b>{text_prich}</b>\n"
                                       f"  🕐Время: {time_vid}</blockquote>",parse_mode='HTML')
                
            if coint_id == 2:
                chek = await check_user(id_reply)
                username = chek['username']
                
                chek_adm = await check_user(id)
                username_adm = chek_adm['username']
                
                await bot.send_message(chat_id=chat_id, text=f"🚨Выдан варн (2/3)\n"
                                       f"  <blockquote>🌵Пользователю: {username}\n"
                                       f"  👤Администратором: {username_adm}\n"
                                       f"  🛑Причина: <b>{text_prich}</b>\n"
                                       f"  🕐Время: {time_vid}</blockquote>",parse_mode='HTML')
        
        if text == 'WARNKIK':
            text_red=f"🚨Кикнут пользователь по варнам(3/3):\n"
            i = 3
            while i != 0:
                if i == 3:
                    chek = await check_user(id_reply)
                    warn_text = chek['warn_text_1']
                    parts = warn_text.split('!', 2)
                    prichina = f"{parts[0].strip()}"
                    admin_id_bd = f"{parts[1].strip()}"
                    chek_adm = await check_user(admin_id_bd)
                    admin = chek_adm['username']
                    time = f"{parts[2].strip()}"
                    text_red += f'<blockquote>⚠️1-предупреждение:\n'
                    text_red += f'    👤Админ: {admin}\n'
                    text_red += f'    🛑Причина: <b>{prichina}</b>\n'
                    text_red += f'    🕐Дата: {time}</blockquote>\n'
                    i -= 1
                    
                if i == 2:
                    chek = await check_user(id_reply)
                    warn_text = chek['warn_text_2']
                    parts = warn_text.split('!', 2)
                    prichina = f"{parts[0].strip()}"
                    admin_id_bd = f"{parts[1].strip()}"
                    chek_adm = await check_user(admin_id_bd)
                    admin = chek_adm['username']
                    time = f"{parts[2].strip()}"
                    text_red += f'<blockquote>⚠️2-предупреждение:\n'
                    text_red += f'    👤Админ: {admin}\n'
                    text_red += f'    🛑Причина: <b>{prichina}</b>\n'
                    text_red += f'    🕐Дата: {time}</blockquote>\n'
                    i -= 1
                    
                if i == 1:
                    chek = await check_user(id_reply)
                    warn_text = chek['warn_text_3']
                    parts = warn_text.split('!', 2)
                    prichina = f"{parts[0].strip()}"
                    admin_id_bd = f"{parts[1].strip()}"
                    chek_adm = await check_user(admin_id_bd)
                    admin = chek_adm['username']
                    time = f"{parts[2].strip()}"
                    text_red += f'<blockquote>⚠️3-предупреждение:\n'
                    text_red += f'  👤Админ: {admin}\n'
                    text_red += f'  🛑Причина: <b>{prichina}</b>\n'
                    text_red += f'  🕐Дата: {time}</blockquote>\n'
                    i -= 1
                    
            await dell_user_bd(id_reply)
                    
            await bot.send_message(chat_id=chat_id, text=text_red, parse_mode='HTML')
            
        if text == 'KIK':
            chek_user = await check_user(id_reply)
            user = chek_user['username']
            chek_admin = await check_user(id)
            admin = chek_admin['username']
            await bot.send_message(chat_id=chat_id, text=f'🚷Кикнут {user} администратором {admin}, по причине: {text_prich}', parse_mode='HTML')
            await dell_user_bd(id_reply)
            
            
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"Ошибка при проверке: {e}")

    
@dp.message(Command('варн'))
async def warn(message: types.Message):
    try:
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        bot_id_1 = await message.bot.get_me()
        bot_id_2 = bot_id_1.id
        chat_type = message.chat.type
        user_id = message.from_user.id
        chat_id = message.chat.id
        user_status_0 = await bot.get_chat_member(chat_id, message.from_user.id)
        user_status = user_status_0.status
    
        if chat_type != 'private':
            if message.reply_to_message:
                user_id_reply = message.reply_to_message.from_user.id
                coint = await check_warn(user_id_reply)
                user_name = message.reply_to_message.from_user.username
                status_bd = await get_role(user_id)
                status_reply_message_bd = await get_role(user_id_reply)
                member = await bot.get_chat_member(beseda, user_id_reply)
                if member.status in ['member', 'administrator', 'creator']:
                    if status_bd:
                        for stat in status_bd:
                            status_1 = stat['user_role']
                        status = status_1
                        if status in ['tex', 'admin', 'moder', 'moder_stazh'] or user_status == 'creator':
                            if user_id_reply != bot_id_2:
                                if user_id != user_id_reply:
                                    if status_reply_message_bd:
                                        for stat_rep in status_reply_message_bd:
                                            status_reply_message_1 = stat_rep['user_role']
                                        status_reply_message = status_reply_message_1
                                
                                        user_status_reply_message_0 = await bot.get_chat_member(chat_id, message.reply_to_message.from_user.id)
                                        user_status_reply_message = user_status_reply_message_0.status
                                        if status_reply_message not in ['tex', 'admin', 'moder', 'moder_stazh'] and user_status_reply_message != 'creator':
                                            if len(message.text.split()) == 2:
                                                text = message.text.split()[1]
                                                text += f' ! {user_id}'
                                                text += f' ! {formatted_time}'
                                                coint += 1
                                                if coint != 3:
                                                    username = message.reply_to_message.from_user.username
                                                    await set_warn(coint, text, user_id_reply)
                                                    text_func = 'WARN'
                                                    await avto_message_warning(text_func, user_id, user_id_reply, formatted_time, message.text.split()[1])
                                                    await message.answer(f"Выдан варн [{"Пользователю"}](https://t.me/{username})\n Причина: {message.text.split()[1]}", parse_mode='Markdown', disable_web_page_preview=True)
                                                    return
                                                else:
                                                    if coint == 3:
                                                        username = message.reply_to_message.from_user.username
                                                        await message.answer(f'[{"Пользователь"}](https://t.me/{username}) кикнут иза максимального количества варнов.', parse_mode='Markdown', disable_web_page_preview=True)
                                                        text_func = 'WARNKIK'
                                                        await set_warn(coint, text, user_id_reply)
                                                        await avto_message_warning(text_func, user_id, user_id_reply, formatted_time, message.text.split()[1])
                                                        await bot.ban_chat_member(chat_id, user_id_reply, revoke_messages=True)
                                                    else:
                                                        if coint > 3:
                                                            await message.answer("У пользователя уже 3 варна.")
                                                            return
                                            else:
                                                await message.answer("Вы не правильно ввели команду\n"
                                                                     "Пример:\n"
                                                                     "/варн (причина)")
                                                return
                                        else:
                                            await message.answer("У администраторов не может быть варна:)")
                                            return
                                    
                                    else:
                                        await message.answer("Не могу найти пользователя.")
                                        return
                            
                                else:
                                    await message.answer("Вы не можете дать варн самому себе.")
                                    return
                        
                            else:
                                await message.answer("Я не могу иметь варна")
                                return
                    
                        else:
                            await message.answer("Команда доступна только модераторам и выше.")
                            return
                
                    else:
                        await message.answer("Ошибка в бд.")
                        return
                
                else:
                    await message.answer("Пользователя нет в беседе.")
                    return
            
            else:
                await message.answer("Вы должны ответить на сообщение пользователя.")
                return
        
        else:
            await message.answer("Данная команда не доступна в личных сообщениях.")
            return
        
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"Ошибка при проверке: {e}")

                                
 
@dp.message(Command('варнлист'))
async def warn(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    chat_type = message.chat.type
    
    try:                         
                                    
        if chat_type != 'private':
            if message.reply_to_message:
                user_id_reply = message.reply_to_message.from_user.id
                chek_us = await check_user(user_id_reply)
                username = chek_us['username']
                koint = await check_warn(user_id_reply)
                text_red=f"🚨Варны пользователя: ({koint}/3)\n"
                if koint != 0:
                    while koint != 0:
                        print(koint)
                        if koint == 2:
                            chek = await check_user(user_id_reply)
                            warn_text = chek['warn_text_1']
                            parts = warn_text.split('!', 2)
                            prichina = f"{parts[0].strip()}"
                            admin_id_bd = f"{parts[1].strip()}"
                            chek_adm = await check_user(admin_id_bd)
                            admin = chek_adm['username']
                            time = f"{parts[2].strip()}"
                            text_red += f'<blockquote>⚠️1-предупреждение:\n'
                            text_red += f'    👤Админ: {admin}\n'
                            text_red += f'    🛑Причина: <b>{prichina}</b>\n'
                            text_red += f'    🕐Дата: {time}</blockquote>\n'
                            koint -= 1
                            
                            if koint == 1:
                                chek = await check_user(user_id_reply)
                                warn_text = chek['warn_text_2']
                                parts = warn_text.split('!', 2)
                                prichina = f"{parts[0].strip()}"
                                admin_id_bd = f"{parts[1].strip()}"
                                chek_adm = await check_user(admin_id_bd)
                                admin = chek_adm['username']
                                time = f"{parts[2].strip()}"
                                text_red += f'<blockquote>⚠️2-предупреждение:\n'
                                text_red += f'    👤Админ: {admin}\n'
                                text_red += f'    🛑Причина: <b>{prichina}</b>\n'
                                text_red += f'    🕐Дата: {time}</blockquote>\n'
                                koint -= 1
                            
                    
                        if koint == 1:
                            chek = await check_user(user_id_reply)
                            warn_text = chek['warn_text_1']
                            if warn_text:
                                parts = warn_text.split('!', 2)
                                prichina = f"{parts[0].strip()}"
                                admin_id_bd = f"{parts[1].strip()}"
                                chek_adm = await check_user(admin_id_bd)
                                admin = chek_adm['username']
                                time = f"{parts[2].strip()}"
                                text_red += f'<blockquote>⚠️1-предупреждение:\n'
                                text_red += f'    👤Админ: {admin}\n'
                                text_red += f'    🛑Причина: <b>{prichina}</b>\n'
                                text_red += f'    🕐Дата: {time}</blockquote>\n'
                                koint -= 1
                            
                            else:
                                warn_text = chek['warn_text_2']
                                if warn_text:
                                    parts = warn_text.split('!', 2)
                                    prichina = f"{parts[0].strip()}"
                                    admin_id_bd = f"{parts[1].strip()}"
                                    chek_adm = await check_user(admin_id_bd)
                                    admin = chek_adm['username']
                                    time = f"{parts[2].strip()}"
                                    text_red += f'<blockquote>⚠️1-предупреждение:\n'
                                    text_red += f'    👤Админ: {admin}\n'
                                    text_red += f'    🛑Причина: <b>{prichina}</b>\n'
                                    text_red += f'    🕐Дата: {time}</blockquote>\n'
                                    koint -= 1
                                
                            
                        
                    await bot.send_message(chat_id=chat_id, text=text_red, parse_mode='HTML')
                    return
            
                else:
                    await bot.send_message(chat_id=chat_id, text="Пользователь не имеет варнов.")
                    return
            
            else:
                await bot.send_message(chat_id=chat_id, text="Нужно ответить командой на сообщение пользователя!")
                return
        
        else:
            await bot.send_message(chat_id=chat_id, text="Данная команда не досутпна в личных сообщениях со мной.")
            return
        
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"Ошибка при проверке: {e}")
    
    
@dp.message(Command('кик'))
async def warn(message: types.Message):
    chat_id = message.chat.id
    bot_id_1 = await message.bot.get_me()
    bot_id_2 = bot_id_1.id
    user_id = message.from_user.id
    chat_type = message.chat.type
    user_status_0 = await bot.get_chat_member(chat_id, message.from_user.id)
    user_status = user_status_0.status
    
    try:
    
        if chat_type != 'private':
            status_bd = await get_role(user_id)
            if status_bd:
                for stat in status_bd:
                    status_1 = stat['user_role']
                status = status_1
                if status in ['tex', 'admin', 'moder', 'moder_stazh'] or user_status == 'creator':
                    if message.reply_to_message:
                        user_id_reply_message = message.reply_to_message.from_user.id
                        status_reply_message_bd = await get_role(user_id_reply_message)
                        if user_id_reply_message != bot_id_2:
                            if user_id != user_id_reply_message:
                                if status_reply_message_bd:
                                    for stat_rep in status_reply_message_bd:
                                        status_reply_message_1 = stat_rep['user_role']
                                    status_reply_message = status_reply_message_1
                                
                                    user_status_reply_message_0 = await bot.get_chat_member(chat_id, message.reply_to_message.from_user.id)
                                    user_status_reply_message = user_status_reply_message_0.status
                                    if status_reply_message not in ['tex', 'admin', 'moder', 'moder_stazh'] and user_status_reply_message != 'creator':
                                        if len(message.text.split()) == 2:
                                            await bot.ban_chat_member(chat_id, user_id_reply_message, revoke_messages=True)
                                            formatted_time = 0
                                            text_func = 'KIK'
                                            await avto_message_warning(text_func, user_id, user_id_reply_message, formatted_time, message.text.split()[1])
                                            await bot.send_message(chat_id=chat_id, text=f'Кинкнут пользователь, причина: {message.text.split()[1]} ')
                                        
                                        else:
                                            await message.answer("Вы не правильно ввели команду\n"
                                                                 "Пример:\n"
                                                                 "/варн (причина)")
                                            return
                                    else:
                                        await message.answer("У администраторов не может быть варна:)")
                                        return
                                    
                                else:
                                    await message.answer("Не могу найти пользователя.")
                                    return
                            
                            else:
                                await message.answer("Вы не можете дать варн самому себе.")
                                return
                        
                        else:
                            await message.answer("Я не могу иметь варна")
                            return
                
                    else:
                        await message.answer("Вы должны ответить на сообщение пользователя.")
                        return
            
                else:
                    await message.answer("Команда доступна только модераторам и выше.")
                    return    
            
            else:
                await message.answer("Ошибка в бд.")
                return
            
        else:
            await message.answer("Данная команда не доступна в личных сообщениях.")
            return
        
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"Ошибка при проверке: {e}")

@dp.message()
async def handle_command_with_prefix(message: types.Message):
    try:
        if message.text and message.text.startswith(COMMAND_PREFIX):
            command = message.text[len(COMMAND_PREFIX):]
            command_parts = command.split(' ', 1)
        
            if command_parts[0] == 'варн':
                global user_id_unwarn, chat_id_unwarn, message_id_unwarn
                bot_id_1 = await message.bot.get_me()
                bot_id_2 = bot_id_1.id
                chat_type = message.chat.type
                chat_id = message.chat.id
            
                if chat_type != 'private':
                    if message.reply_to_message:
                        if len(message.text.split()) == 2:
                            user_id_reply = message.reply_to_message.from_user.id
                            print(f'{user_id_reply} {bot_id_2}')
                            if user_id_reply != bot_id_2:
                                koint = await check_warn(user_id_reply)
                                if koint != 0:
                                    if koint == 2:
                                        user_id_unwarn = user_id_reply
                                        sent_message = await message.answer(text=f'Пользователь имеет ({koint}/3) варна.\n'
                                                             f'Выберите колличество, которое хотите снять.',reply_markup=Button.button_unwarn_all)
                                        message_id_unwarn = sent_message.message_id
                                        chat_id_unwarn = message.chat.id
                            
                                    if koint == 1:
                                        user_id_unwarn = user_id_reply
                                        await message.answer('Пользователь имеет 1 варн.\n'
                                                             f'Нажмите кнопку внизу, чтобы снять варн.',reply_markup=Button.button_unwarn)
                        
                            else:
                                await message.answer("Я не могу иметь варна")
                                return   
                    
                        else:
                            await message.answer("Вы не правильно ввели команду\n"
                                                 "Пример:\n"
                                                 "/варн (причина)")
                            return
                    
                    else:
                        await bot.send_message(chat_id=chat_id, text="Нужно ответить командой на сообщение пользователя!")
                        return
            
                else:
                    await bot.send_message(chat_id=chat_id, text="Данная команда не досутпна в личных сообщениях со мной.")
                    return
                
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"Ошибка при проверке: {e}")
                
@dp.callback_query(lambda c: c.data in ['one', 'two', 'all', 'un'])
async def knopki_admin(callback_query: types.CallbackQuery):
    data = callback_query.data
    global user_id_unwarn, chat_id_unwarn, message_id_unwarn
    
    await bot.answer_callback_query(callback_query.id)
    
    if data == 'one':
        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id
        user_status_0 = await bot.get_chat_member(chat_id, user_id)
        user_status = user_status_0.status
        status_bd = await get_role(user_id)
        if status_bd:
            for stat in status_bd:
                status_1 = stat['user_role']
            status = status_1
            if status in ['tex', 'admin'] or user_status == 'creator':
                koint = 1
                await unwarn_users(koint, user_id_unwarn)
                await bot.edit_message_text(text=f'Варн снят',chat_id=chat_id_unwarn,message_id=message_id_unwarn)
                
                
            else:
                chat_id_user = callback_query.from_user.id
                await bot.send_message(chat_id=chat_id_user, text="Кнопки действуют только на Администраторов и выше!")
                
    if data == 'two':
        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id
        user_status_0 = await bot.get_chat_member(chat_id, user_id)
        user_status = user_status_0.status
        status_bd = await get_role(user_id)
        if status_bd:
            for stat in status_bd:
                status_1 = stat['user_role']
            status = status_1
            if status in ['tex', 'admin'] or user_status == 'creator':
                koint = 2
                await unwarn_users(koint, user_id_unwarn)
                await bot.edit_message_text(text=f'Варн снят',chat_id=chat_id_unwarn,message_id=message_id_unwarn)
                
                
            else:
                chat_id_user = callback_query.from_user.id
                await bot.send_message(chat_id=chat_id_user, text="Кнопки действуют только на Администраторов и выше!")       
                
                

                                        
                      
                                        
                                            
                                        


async def main() -> None:
    bot = Bot(token=tg_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    #task1 = asyncio.create_task(handle_message(Message))
    task2 = asyncio.create_task(periodic_check())
    await dp.start_polling(bot)
    #await task1
    await task2

    dp.message.register(start, Command('start'))
    


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот отключен!")