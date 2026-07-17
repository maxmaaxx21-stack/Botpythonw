import logging
import subprocess
import os
import time
import asyncio
import random
import json
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.request import HTTPXRequest
# Backup Command - Add this after start command handler
import zipfile
import io

# --- CONFIGURATION ---
TOKEN = "8744557129:AAGXAV4F8WWE1kCKBh3WyVhbP8sbYgCzjzk"
OWNER_ID = 8433640436
ADMIN_IDS = [8433640436]
CH_LINK = "https://t.me/PRIMEXHOST"
OWNER_LINK = "https://t.me/PRIMEXHOSTS"

# ============================================
# 🎯 PREMIUM EMOJI IDS
# ============================================
PREMIUM_EMOJI_STOP = "5834895792409677476"
PREMIUM_EMOJI_RESTART = "6122764622509380932"
PREMIUM_EMOJI_DELETE = "5307659638810877853"
PREMIUM_EMOJI_LOGS = "6172332822892647766"
PREMIUM_EMOJI_BACK = "5983279327574233274"
PREMIUM_EMOJI_CONFIRM = "5307659638810877853"
PREMIUM_EMOJI_CANCEL = "6172332822892647766"
PREMIUM_EMOJI_UPLOAD = "6096080291347042802"
PREMIUM_EMOJI_CHECK = "5931760374519959889"
PREMIUM_EMOJI_SPEED = "5188481279963715781"
PREMIUM_EMOJI_STATS = "6255952172538662138"
PREMIUM_EMOJI_CONTACT = "6170400139149055154"
PREMIUM_EMOJI_ADMIN = "5364125616801073577"
PREMIUM_EMOJI_UPDATES = "5298609030321691620"

# Database files
USER_DATA_FILE = "user_data.json"
FILES_DB_FILE = "files_database.json"
SETTINGS_FILE = "bot_settings.json"

# Default settings
DEFAULT_USER_LIMIT = 5

# Load/Save functions
def load_json(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except:
        pass
    return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# Load data
settings = load_json(SETTINGS_FILE, {"global_limit": DEFAULT_USER_LIMIT})
all_files_db = load_json(FILES_DB_FILE, {})
user_data = load_json(USER_DATA_FILE, {"users": [], "total_files": 0})

# Tracking
running_processes = {}
all_users = set(user_data.get("users", []))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- HTTP Request ---
request = HTTPXRequest(
    connection_pool_size=20,
    read_timeout=30,
    write_timeout=30,
    connect_timeout=30,
    pool_timeout=30
)

# ============================================
# 🎨 FORMATTING FUNCTIONS
# ============================================
def b(text):
    return f"<b>{text}</b>"

def i(text):
    return f"<i>{text}</i>"

def mono(text):
    text = str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return f"<code>{text}</code>"

def progress_bar(percent):
    filled = int(percent / 10)
    empty = 10 - filled
    return f"▰" * filled + f"▱" * empty

# ============================================
# 🎯 COLORED REPLY KEYBOARD BUTTONS
# ============================================
def main_menu(user_id):
    updates_btn = KeyboardButton(
        text="Updates Channel",
        style="success",
        icon_custom_emoji_id=PREMIUM_EMOJI_UPDATES
    )
    
    upload_btn = KeyboardButton(
        text="Upload File",
        style="primary",
        icon_custom_emoji_id=PREMIUM_EMOJI_UPLOAD
    )
    
    check_btn = KeyboardButton(
        text="Check Files",
        style="primary",
        icon_custom_emoji_id=PREMIUM_EMOJI_CHECK
    )
    
    speed_btn = KeyboardButton(
        text="Bot Speed",
        style="primary",
        icon_custom_emoji_id=PREMIUM_EMOJI_SPEED
    )
    
    stats_btn = KeyboardButton(
        text="Statistics",
        style="primary",
        icon_custom_emoji_id=PREMIUM_EMOJI_STATS
    )
    
    contact_btn = KeyboardButton(
        text="Contact Owner",
        style="primary",
        icon_custom_emoji_id=PREMIUM_EMOJI_CONTACT
    )
    
    keyboard = [
        [updates_btn],
        [upload_btn, check_btn],
        [speed_btn, stats_btn],
        [contact_btn]
    ]
    
    if user_id == OWNER_ID or user_id in ADMIN_IDS:
        admin_btn = KeyboardButton(
            text="Admin Panel",
            style="danger",
            icon_custom_emoji_id=PREMIUM_EMOJI_ADMIN
        )
        keyboard.append([admin_btn])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ============================================
# 🚀 START COMMAND
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    all_users.add(user.id)
    
    user_data["users"] = list(all_users)
    save_json(USER_DATA_FILE, user_data)
    
    global_limit = settings.get("global_limit", DEFAULT_USER_LIMIT)
    files_count = len(running_processes.get(user.id, []))
    
    if user.id == OWNER_ID or user.id in ADMIN_IDS:
        display_limit = "∞ Unlimited"
        status = "OWNER" if user.id == OWNER_ID else "ADMIN"
    else:
        display_limit = str(global_limit)
        status = "FREE"
    
    welcome_text = f"""
<tg-emoji emoji-id='6237867138997034625'>📌</tg-emoji> {b('Welcome,')} {b(user.first_name)}

<tg-emoji emoji-id='6237547619200014867'>📌</tg-emoji> {b('Your User ID:')} {mono(str(user.id))} 
<tg-emoji emoji-id='6237621548472081271'>📌</tg-emoji> {b('Username:')} @{user.username if user.username else 'N/A'} 
<tg-emoji emoji-id='6237853377921817790'>📌</tg-emoji> {b('Your Status:')} {b(status)}
<tg-emoji emoji-id='6240032124636765022'>📌</tg-emoji> {b('Files Uploaded:')} {b(str(files_count))} / {b(display_limit)}

{i('Host & run Python (.py) or JS (.js) scripts.')}
{i('Use colored buttons below.')}
    """
    
    try:
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            await update.message.reply_photo(
                photo=photos.photos[0][-1].file_id, 
                caption=welcome_text, 
                parse_mode="HTML",
                reply_markup=main_menu(user.id)
            )
        else:
            await update.message.reply_text(
                welcome_text, 
                parse_mode="HTML",
                reply_markup=main_menu(user.id)
            )
    except Exception as e:
        logging.error(f"Error in start: {e}")
        await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=main_menu(user.id))
        
        # ============================================
# 📦 BACKUP COMMAND
# ============================================
async def backup_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Owner only!")
        return
    
    msg = await update.message.reply_text("📦 Creating backup...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in ['user_data.json', 'files_database.json', 'bot_settings.json']:
            if os.path.exists(file):
                zip_file.write(file)
        for item in os.listdir('.'):
            if item.startswith('user_') and (item.endswith('.py') or item.endswith('.js') or item.endswith('.log')):
                zip_file.write(item)
    
    zip_buffer.seek(0)
    await msg.delete()
    await context.bot.send_document(chat_id=user_id, document=zip_buffer, filename=f"backup_{timestamp}.zip", caption="✅ Backup Complete!")

# ============================================
# 📁 CHECK FILES
# ============================================
async def check_files_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    files = running_processes.get(user_id, [])
    
    if not files:
        await update.message.reply_text(
            f"{b('Your files:')}\n\n{i('No active scripts running.')}",
            parse_mode="HTML"
        )
        return

    text = f"{b('Your files:')}\n\n{i('Click to manage.')}"
    
    keyboard = []
    for idx, f in enumerate(files):
        is_running = False
        if f['proc']:
            try:
                is_running = f['proc'].poll() is None
            except:
                is_running = False
        
        status = "🟢 Running" if is_running else "🔴 Stopped"
        file_ext = "py" if f['name'].endswith('.py') else "js"
        btn_text = f"{f['name']} ({file_ext}) - {status}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"manage_{idx}")])
    
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================
# ⚙️ CONTROL PANEL
# ============================================
async def control_panel(update: Update, context: ContextTypes.DEFAULT_TYPE, file_idx):
    query = update.callback_query
    user_id = query.from_user.id
    file_data = running_processes[user_id][file_idx]
    
    is_running = False
    if file_data['proc']:
        try:
            is_running = file_data['proc'].poll() is None
        except:
            is_running = False
    
    status = "🟢 Running" if is_running else "🔴 Stopped"
    
    text = f"""
{b('Controls for:')} {b(file_data['name'])} {i('of User')} {mono(str(user_id))}
{b('Status:')} {status}
    """

    keyboard = [
        [
            InlineKeyboardButton(
                text="Stop",
                callback_data=f"stop_{file_idx}",
                style="danger",
                icon_custom_emoji_id=PREMIUM_EMOJI_STOP
            ),
            InlineKeyboardButton(
                text="Restart",
                callback_data=f"restart_{file_idx}",
                style="primary",
                icon_custom_emoji_id=PREMIUM_EMOJI_RESTART
            )
        ],
        [
            InlineKeyboardButton(
                text="Delete",
                callback_data=f"delete_{file_idx}",
                style="danger",
                icon_custom_emoji_id=PREMIUM_EMOJI_DELETE
            ),
            InlineKeyboardButton(
                text="Logs",
                callback_data=f"logs_{file_idx}",
                style="primary",
                icon_custom_emoji_id=PREMIUM_EMOJI_LOGS
            )
        ],
        [
            InlineKeyboardButton(
                text="Back to Files",
                callback_data="back_to_files",
                style="success",
                icon_custom_emoji_id=PREMIUM_EMOJI_BACK
            )
        ]
    ]
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================
# 📤 FILE UPLOAD HANDLER
# ============================================
async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    doc = update.message.document
    user = update.effective_user
    
    if not doc.file_name.endswith(('.py', '.js')):
        await update.message.reply_text(
            f"{b('Invalid File!')}\n\n{i('Only .py and .js files are supported.')}",
            parse_mode="HTML"
        )
        return

    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        global_limit = settings.get("global_limit", DEFAULT_USER_LIMIT)
        files_count = len(running_processes.get(user_id, []))
        
        if files_count >= global_limit:
            await update.message.reply_text(
                f"{b('Limit Reached!')}\n\n{i(f'You can only host {global_limit} files. Delete some files first.')}",
                parse_mode="HTML"
            )
            return

    try:
        # Animation
        anim_msg = await update.message.reply_text(f"{b('Launching...')}\n\n{mono('▱▱▱▱▱▱▱▱▱▱')} 0%", parse_mode="HTML")
        
        for percent in range(10, 101, 10):
            await anim_msg.edit_text(f"{b('Launching...')}\n\n{mono(progress_bar(percent))} {percent}%", parse_mode="HTML")
            await asyncio.sleep(0.3)

        # Download file
        file = await context.bot.get_file(doc.file_id)
        file_path = f"user_{user_id}_{doc.file_name}"
        await file.download_to_drive(file_path)
        
        # Make file executable
        os.chmod(file_path, 0o755)
        
        # Start process
        log_file = open(f"{file_path}.log", "w")
        
        if file_path.endswith('.py'):
            cmd = ["python3", "-u", file_path]
        else:
            cmd = ["node", file_path]
        
        process = subprocess.Popen(
            cmd, 
            stdout=log_file, 
            stderr=log_file,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Store process
        if user_id not in running_processes: 
            running_processes[user_id] = []
        
        file_info = {
            "name": doc.file_name,
            "proc": process,
            "path": file_path,
            "log": log_file,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        running_processes[user_id].append(file_info)
        
        # Save to database
        file_id = f"{user_id}_{doc.file_name}_{int(time.time())}"
        all_files_db[file_id] = {
            "user_id": user_id,
            "username": user.username if user.username else "NoUsername",
            "name": doc.file_name,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "running",
            "path": file_path
        }
        save_json(FILES_DB_FILE, all_files_db)
        
        user_data["total_files"] = user_data.get("total_files", 0) + 1
        save_json(USER_DATA_FILE, user_data)
        
        await anim_msg.delete()
        
        # Admin notification
        admin_notify = f"""
<b>📁 New File Running!</b>

<b>👤 User:</b> {user.full_name}
<b>🆔 User ID:</b> {mono(str(user_id))}
<b>📝 Username:</b> @{user.username if user.username else 'N/A'}
<b>📄 File Name:</b> {doc.file_name}
<b>⏰ Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
<b>📊 Status:</b> Running
        """
        
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_notify,
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"Failed to notify admin: {e}")
        
        # User success message
        await update.message.reply_text(
            f"<tg-emoji emoji-id='6239781418805762425'>📌</tg-emoji> {b('Script Running Successfully!')}\n\n"
            f"<tg-emoji emoji-id='6093612746736145083'>📌</tg-emoji> {b('File:')} {mono(doc.file_name)}\n"
            f"<tg-emoji emoji-id='6093612746736145083'>📌</tg-emoji> {b('File ID:')} {mono(file_id)}\n\n"
            f"<tg-emoji emoji-id='6089003761496232797'>📌</tg-emoji> {i('Use Check Files button to manage your scripts.')}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        await update.message.reply_text(
            f"{b('Error:')}\n\n{mono(str(e))}",
            parse_mode="HTML"
        )

# ============================================
# 📢 BROADCAST COMMAND
# ============================================
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await update.message.reply_text(f"{b('Access Denied!')}", parse_mode="HTML")
        return
    
    if not context.args:
        await update.message.reply_text(
            f"{b('Usage:')}\n\n/broadcast <message>",
            parse_mode="HTML"
        )
        return
    
    msg = " ".join(context.args)
    success = 0
    fail = 0
    
    status_msg = await update.message.reply_text(f"{b('Sending broadcast...')}", parse_mode="HTML")
    
    for uid in all_users:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 {b('Announcement')}\n\n{msg}",
                parse_mode="HTML"
            )
            success += 1
            await asyncio.sleep(0.05)
        except:
            fail += 1
    
    await status_msg.edit_text(
        f"{b('Broadcast Completed!')}\n\n"
        f"Sent: {success}\nFailed: {fail}",
        parse_mode="HTML"
    )

# ============================================
# 🎯 CALLBACK HANDLER
# ============================================
async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    await query.answer()
    
    if data == "back_to_files":
        files = running_processes.get(user_id, [])
        text = f"{b('Your files:')}\n\n{i('Click to manage.')}"
        keyboard = []
        for idx, f in enumerate(files):
            is_running = False
            if f['proc']:
                try:
                    is_running = f['proc'].poll() is None
                except:
                    is_running = False
            status = "🟢 Running" if is_running else "🔴 Stopped"
            file_ext = "py" if f['name'].endswith('.py') else "js"
            btn_text = f"{f['name']} ({file_ext}) - {status}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"manage_{idx}")])
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    if data == "back_to_admin":
        await show_admin_panel(update, context)
        return
    
    if data == "back_to_main":
        await start(update, context)
        return
    
    if data.startswith("manage_"):
        idx = int(data.split("_")[1])
        await control_panel(update, context, idx)
    
    elif data.startswith("stop_"):
        idx = int(data.split("_")[1])
        if user_id in running_processes and idx < len(running_processes[user_id]):
            proc = running_processes[user_id][idx]['proc']
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.kill()
                except:
                    pass
            for file_id, file_info in all_files_db.items():
                if file_info["user_id"] == user_id and file_info["name"] == running_processes[user_id][idx]['name']:
                    file_info["status"] = "stopped"
                    save_json(FILES_DB_FILE, all_files_db)
                    break
            await query.edit_message_text(f"{b('Process Stopped!')}", parse_mode="HTML")
            await asyncio.sleep(1)
            await control_panel(update, context, idx)
    
    elif data.startswith("restart_"):
        idx = int(data.split("_")[1])
        if user_id in running_processes and idx < len(running_processes[user_id]):
            proc = running_processes[user_id][idx]['proc']
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.kill()
                except:
                    pass
            file_path = running_processes[user_id][idx]['path']
            log_file = open(f"{file_path}.log", "w")
            if file_path.endswith('.py'):
                cmd = ["python3", "-u", file_path]
            else:
                cmd = ["node", file_path]
            running_processes[user_id][idx]['proc'] = subprocess.Popen(cmd, stdout=log_file, stderr=log_file, start_new_session=True)
            running_processes[user_id][idx]['log'] = log_file
            for file_id, file_info in all_files_db.items():
                if file_info["user_id"] == user_id and file_info["name"] == running_processes[user_id][idx]['name']:
                    file_info["status"] = "running"
                    save_json(FILES_DB_FILE, all_files_db)
                    break
            await query.edit_message_text(f"{b('Process Restarted!')}", parse_mode="HTML")
            await asyncio.sleep(1)
            await control_panel(update, context, idx)
    
    elif data.startswith("delete_"):
        idx = int(data.split("_")[1])
        if user_id in running_processes and idx < len(running_processes[user_id]):
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="Confirm",
                        callback_data=f"confirm_del_{idx}",
                        style="danger",
                        icon_custom_emoji_id=PREMIUM_EMOJI_CONFIRM
                    ),
                    InlineKeyboardButton(
                        text="Cancel",
                        callback_data=f"manage_{idx}",
                        style="primary",
                        icon_custom_emoji_id=PREMIUM_EMOJI_CANCEL
                    )
                ]
            ]
            await query.edit_message_text(
                f"{b('Are you sure?')}\n\n{i('This action cannot be undone.')}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    elif data.startswith("confirm_del_"):
        idx = int(data.split("_")[2])
        if user_id in running_processes and idx < len(running_processes[user_id]):
            file_data = running_processes[user_id][idx]
            if file_data['proc'] and file_data['proc'].poll() is None:
                file_data['proc'].terminate()
                try:
                    file_data['proc'].kill()
                except:
                    pass
            if 'log' in file_data:
                try:
                    file_data['log'].close()
                except:
                    pass
            if os.path.exists(file_data['path']):
                os.remove(file_data['path'])
            log_path = f"{file_data['path']}.log"
            if os.path.exists(log_path):
                os.remove(log_path)
            for file_id, file_info in list(all_files_db.items()):
                if file_info["user_id"] == user_id and file_info["name"] == file_data['name']:
                    del all_files_db[file_id]
                    save_json(FILES_DB_FILE, all_files_db)
                    break
            running_processes[user_id].pop(idx)
            await query.edit_message_text(f"{b('File Deleted Successfully!')}", parse_mode="HTML")
            await asyncio.sleep(1)
            await check_files_menu(update, context)
    
    elif data.startswith("logs_"):
        idx = int(data.split("_")[1])
        if user_id in running_processes and idx < len(running_processes[user_id]):
            file_data = running_processes[user_id][idx]
            log_file_path = f"{file_data['path']}.log"
            
            if os.path.exists(log_file_path):
                try:
                    with open(log_file_path, 'r') as f:
                        logs = f.read()
                    
                    if not logs.strip():
                        await query.message.reply_text(f"Log Output:\n\nNo output yet.")
                    else:
                        if len(logs) > 3000:
                            logs = logs[-3000:]
                        await query.message.reply_text(f"Log Output:\n\n{logs}")
                except Exception as e:
                    await query.message.reply_text(f"Error reading logs:\n\n{str(e)}")
            else:
                await query.message.reply_text(f"No log file found.")
            
            await control_panel(update, context, idx)
    
    elif data == "admin_panel":
        await show_admin_panel(update, context)
    elif data == "admin_users":
        await admin_users(update, context)
    elif data == "admin_all_files":
        await admin_all_files(update, context)
    elif data == "admin_user_files":
        await admin_user_files(update, context)
    elif data == "admin_limit":
        await admin_change_limit(update, context)
    elif data == "admin_stats":
        await admin_stats(update, context)
    elif data == "admin_broadcast":
        await admin_broadcast(update, context)
    elif data.startswith("view_user_files_"):
        target_user = int(data.split("_")[3])
        await view_user_files(update, context, target_user)

# ============================================
# 👑 ADMIN PANEL FUNCTIONS
# ============================================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await update.message.reply_text(f"{b('Access Denied!')}", parse_mode="HTML")
        return
    total_files = sum(len(files) for files in running_processes.values())
    running = 0
    for files in running_processes.values():
        for f in files:
            if f['proc'] and f['proc'].poll() is None:
                running += 1
    global_limit = settings.get("global_limit", DEFAULT_USER_LIMIT)
    text = f"""
{b('ADMIN CONTROL PANEL')}
{b('━━━━━━━━━━━━━━━━━━━━━━')}
{b('Owner ID:')} {mono(str(OWNER_ID))}
{b('Total Users:')} {b(str(len(all_users)))}
{b('Total Files:')} {b(str(total_files))}
{b('Running:')} {b(str(running))}
{b('Stopped:')} {b(str(total_files - running))}
{b('Global Limit:')} {b(str(global_limit))} {i('files/user')}
{b('━━━━━━━━━━━━━━━━━━━━━━')}
{i('Select an option:')}
    """
    keyboard = [
        [InlineKeyboardButton("👥 View All Users", callback_data="admin_users", style="primary")],
        [InlineKeyboardButton("📁 All Hosted Files", callback_data="admin_all_files", style="primary")],
        [InlineKeyboardButton("👤 User's Files", callback_data="admin_user_files", style="primary")],
        [InlineKeyboardButton("📊 Change Global Limit", callback_data="admin_limit", style="success")],
        [InlineKeyboardButton("📈 System Stats", callback_data="admin_stats", style="primary")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast", style="primary")],
        [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main", style="danger")]
    ]
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        await query.edit_message_text(f"{b('Access Denied!')}", parse_mode="HTML")
        return
    total_files = sum(len(files) for files in running_processes.values())
    running = 0
    for files in running_processes.values():
        for f in files:
            if f['proc'] and f['proc'].poll() is None:
                running += 1
    global_limit = settings.get("global_limit", DEFAULT_USER_LIMIT)
    text = f"""
{b('ADMIN CONTROL PANEL')}
{b('━━━━━━━━━━━━━━━━━━━━━━')}
{b('Owner ID:')} {mono(str(OWNER_ID))}
{b('Total Users:')} {b(str(len(all_users)))}
{b('Total Files:')} {b(str(total_files))}
{b('Running:')} {b(str(running))}
{b('Stopped:')} {b(str(total_files - running))}
{b('Global Limit:')} {b(str(global_limit))} {i('files/user')}
{b('━━━━━━━━━━━━━━━━━━━━━━')}
{i('Select an option:')}
    """
    keyboard = [
        [InlineKeyboardButton("👥 View All Users", callback_data="admin_users", style="primary")],
        [InlineKeyboardButton("📁 All Hosted Files", callback_data="admin_all_files", style="primary")],
        [InlineKeyboardButton("👤 User's Files", callback_data="admin_user_files", style="primary")],
        [InlineKeyboardButton("📊 Change Global Limit", callback_data="admin_limit", style="success")],
        [InlineKeyboardButton("📈 System Stats", callback_data="admin_stats", style="primary")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast", style="primary")],
        [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main", style="danger")]
    ]
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = f"{b('ALL USERS')}\n\n"
    users_list = list(all_users)
    for uid in users_list:
        files = len(running_processes.get(uid, []))
        status = "👑" if uid == OWNER_ID else "🛡️" if uid in ADMIN_IDS else "👤"
        text += f"{status} {b(str(uid))} - {i(str(files))} {i('files')}\n"
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel", style="primary")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main", style="danger")]
    ]
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_all_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = f"{b('ALL HOSTED FILES')}\n\n"
    if not all_files_db:
        text += f"{i('No files hosted yet.')}"
    else:
        files_list = list(all_files_db.values())
        for file_info in files_list:
            user = file_info["user_id"]
            name = file_info["name"]
            status = "🟢" if file_info["status"] == "running" else "🔴"
            date = file_info["date"][:10]
            text += f"{status} {b(name)} - {i('User:')} {b(str(user))} ({date})\n"
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel", style="primary")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main", style="danger")]
    ]
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_user_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = f"{b('SELECT USER TO VIEW FILES')}\n\n"
    keyboard = []
    
    # Sab users jo files upload kiye hain
    users_with_files = {}
    for file_id, file_info in all_files_db.items():
        uid = file_info["user_id"]
        if uid not in users_with_files:
            users_with_files[uid] = 0
        users_with_files[uid] += 1
    
    for uid, file_count in users_with_files.items():
        status = "👑" if uid == OWNER_ID else "🛡️" if uid in ADMIN_IDS else "👤"
        btn_text = f"{status} {uid} ({file_count} files)"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"view_user_files_{uid}", style="primary")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel", style="danger")])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def view_user_files(update: Update, context: ContextTypes.DEFAULT_TYPE, target_user):
    query = update.callback_query
    text = f"{b(f'Files of User {target_user}')}\n\n"
    user_files = [f for f in all_files_db.values() if f["user_id"] == target_user]
    if not user_files:
        text += f"{i('No files found for this user.')}"
    else:
        for file_info in user_files:
            name = file_info["name"]
            status = "🟢" if file_info["status"] == "running" else "🔴"
            date = file_info["date"]
            text += f"{status} {b(name)} - {date}\n"
    keyboard = [
        [InlineKeyboardButton("🔙 Back to User List", callback_data="admin_user_files", style="primary")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main", style="danger")]
    ]
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_change_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    current = settings.get("global_limit", DEFAULT_USER_LIMIT)
    text = f"""
{b('CHANGE GLOBAL FILE LIMIT')}
{b('Current Limit:')} {b(str(current))} {i('files per user')}
{i('Admin/Owner: Unlimited')}
{i('Enter new limit (number):')}
    """
    await query.message.reply_text(text, parse_mode="HTML")
    context.user_data["awaiting_limit"] = True

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    total_files = sum(len(files) for files in running_processes.values())
    running = 0
    stopped = 0
    for files in running_processes.values():
        for f in files:
            if f['proc'] and f['proc'].poll() is None:
                running += 1
            else:
                stopped += 1
    text = f"""
{b('SYSTEM STATISTICS')}
{b('━━━━━━━━━━━━━━━━━━━━━━')}
{b('Total Users:')} {b(str(len(all_users)))}
{b('Owner ID:')} {mono(str(OWNER_ID))}
{b('Admins:')} {b(str(len(ADMIN_IDS)))}
{b('━━━━━━━━━━━━━━━━━━━━━━')}
{b('Total Files:')} {b(str(total_files))}
{b('Running:')} {b(str(running))}
{b('Stopped:')} {b(str(stopped))}
{b('━━━━━━━━━━━━━━━━━━━━━━')}
{b('Global Limit:')} {b(str(settings.get('global_limit', DEFAULT_USER_LIMIT)))}
{b('Last Updated:')} {i(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
{b('━━━━━━━━━━━━━━━━━━━━━━')}
    """
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel", style="primary")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main", style="danger")]
    ]
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        f"{b('Broadcast Mode')}\n\nSend your message:",
        parse_mode="HTML"
    )
    context.user_data["awaiting_broadcast"] = True

# ============================================
# 📝 TEXT HANDLER
# ============================================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # Check for broadcast input
    if context.user_data.get("awaiting_broadcast"):
        if text.lower() == "/cancel":
            del context.user_data["awaiting_broadcast"]
            await update.message.reply_text(f"{b('Broadcast cancelled.')}", parse_mode="HTML")
            return
        
        success = 0
        fail = 0
        status_msg = await update.message.reply_text(f"{b('Sending...')}", parse_mode="HTML")
        
        for uid in all_users:
            try:
                await context.bot.send_message(chat_id=uid, text=f"📢 {b('Announcement')}\n\n{text}", parse_mode="HTML")
                success += 1
                await asyncio.sleep(0.05)
            except:
                fail += 1
        
        await status_msg.edit_text(f"{b('Broadcast Done!')}\n\nSent: {success}\nFailed: {fail}", parse_mode="HTML")
        del context.user_data["awaiting_broadcast"]
        return
    
    # Check for limit input
    if context.user_data.get("awaiting_limit"):
        try:
            new_limit = int(text)
            if new_limit > 0:
                settings["global_limit"] = new_limit
                save_json(SETTINGS_FILE, settings)
                await update.message.reply_text(f"{b('Limit Updated!')}\n\nNow users can host {new_limit} files.", parse_mode="HTML")
                del context.user_data["awaiting_limit"]
            else:
                await update.message.reply_text(f"{b('Invalid!')}", parse_mode="HTML")
        except:
            await update.message.reply_text(f"{b('Invalid number!')}", parse_mode="HTML")
        return
    
    # Normal text handling
    if text == "Updates Channel":
        await update.message.reply_text(f"{b('Join:')}\n\n{CH_LINK}", parse_mode="HTML")
    elif text == "Upload File":
        await update.message.reply_text(f"{b('Upload File:')}\n\nSend .py or .js file", parse_mode="HTML")
    elif text == "Check Files":
        await check_files_menu(update, context)
    elif text == "Bot Speed":
        start_time = time.time()
        msg = await update.message.reply_text(f"{b('Checking...')}", parse_mode="HTML")
        ms = (time.time() - start_time) * 1000
        await msg.edit_text(f"{b('Speed:')}\n\n{mono(f'{ms:.2f} ms')}", parse_mode="HTML")
    elif text == "Statistics":
        total_files = sum(len(files) for files in running_processes.values())
        running = 0
        for files in running_processes.values():
            for f in files:
                if f['proc'] and f['proc'].poll() is None:
                    running += 1
        await update.message.reply_text(
            f"{b('Statistics')}\n\nUsers: {len(all_users)}\nTotal Files: {total_files}\nRunning: {running}\nStopped: {total_files - running}",
            parse_mode="HTML"
        )
    elif text == "Contact Owner":
        await update.message.reply_text(f"{b('Contact:')}\n\n{OWNER_LINK}", parse_mode="HTML")
    elif text == "Admin Panel":
        await admin_panel(update, context)

# ============================================
# 🚀 MAIN FUNCTION - FIXED FOR TERMUX/RAILWAY
# ============================================
def main():
    # Create new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        app = Application.builder().token(TOKEN).request(request).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("broadcast", broadcast_command))
        app.add_handler(CommandHandler("backup", backup_now))   # ⭐⭐⭐ YAHAN ADD KARO ⭐⭐⭐
        app.add_handler(CallbackQueryHandler(handle_callbacks))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.add_handler(MessageHandler(filters.Document.ALL, handle_docs))
        print("="*50)
        print("🤖 HOSTING BOT RUNNING")
        print("="*50)
        print(f"Owner: {OWNER_ID}")
        print(f"Token: {TOKEN[:20]}...")
        print("="*50)
        
        # Run with our custom loop
        loop.run_until_complete(app.run_polling())
        
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")
    finally:
        loop.close()

if __name__ == "__main__":
    main()