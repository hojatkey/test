import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
import random
from datetime import datetime, timedelta
import schedule
import time
import threading
import asyncio

# تنظیم لاگینگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class HabitTrackerBot:
    def __init__(self, token, group_chat_id):
        self.ADMIN_PASSWORD = '919'
        self.GROUP_CHAT_ID = group_chat_id
        self.users = {}  # userId -> userData
        self.challenges = []
        self.user_states = {}  # userId -> current state
        self.temp_challenge = None
        self.application = Application.builder().token(token).build()

        # ثبت هندلرها
        self.initialize_bot()

    def initialize_bot(self):
        # ثبت دستورات
        self.application.add_handler(CommandHandler("start", self.show_start_menu))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))

        # برنامه‌ریزی بررسی روزانه
        self.schedule_daily_check()

    # 🎨 UI Helpers
    def create_inline_keyboard(self, buttons):
        keyboard = [[InlineKeyboardButton(btn["text"], callback_data=btn["callback_data"]) for btn in row]
                    if isinstance(row, list) else [InlineKeyboardButton(row["text"], callback_data=row["callback_data"])]
                    for row in buttons]
        return InlineKeyboardMarkup(keyboard)

    def create_button(self, text, data):
        return {"text": text, "callback_data": data}

    # 🌟 دیتابیس کاربر
    def get_user_data(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {
                "name": "",
                "habits": [],
                "score": 0,
                "daily_reports": {},
                "join_date": datetime.now(),
                "challenge_status": None,
                "day_count": 1,
                "username": ""
            }
        return self.users[user_id]

    def get_user_state(self, user_id):
        return self.user_states.get(user_id, "main")

    def set_user_state(self, user_id, state):
        self.user_states[user_id] = state

    # 📅 محاسبه روز کاربر
    def calculate_user_day(self, user_data):
        today = datetime.now()
        join_date = user_data["join_date"]
        return (today - join_date).days + 1

    # 🚀 پیام‌های اصلی
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        text = update.message.text.strip()
        state = self.get_user_state(user_id)
        
        user_data = self.get_user_data(user_id)
        user_data['username'] = update.message.from_user.username if update.message.from_user.username else "آیدی نامشخص"

        if text == "/start":
            await self.show_start_menu(update, context)
            return
            
        # فقط در صورتی که کاربر در یکی از حالت‌های زیر باشد، پیام را پردازش کن
        if state == "register_name":
            await self.handle_name_registration(chat_id, user_id, text)
        elif state in ["add_habits", "add_habits_new"]:
            await self.handle_add_habits(chat_id, user_id, text)
        elif state == "edit_habit":
            await self.handle_edit_habit(chat_id, user_id, text)
        elif state == "change_name":
            await self.handle_change_name_input(chat_id, user_id, text)
        elif state == "admin_password":
            await self.handle_admin_password(chat_id, user_id, text)
        elif state == "challenge_text":
            await self.handle_challenge_text(chat_id, user_id, text)
        elif state == "challenge_duration":
            await self.handle_challenge_duration(chat_id, user_id, text)
        elif state == "challenge_target":
            await self.handle_challenge_target(chat_id, user_id, text)
        else:
            # در بقیه موارد پیام را نادیده بگیر
            pass
            

    # 🎯 منوی شروع
    async def show_start_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
        user_data = self.get_user_data(user_id)
        if update.message and update.message.from_user.username:
             user_data['username'] = update.message.from_user.username

        if not user_data["name"]:
            keyboard = self.create_inline_keyboard([
                [self.create_button("🌟 ثبت نام", "register")],
                [self.create_button("👑 ادمین", "admin")],
                [self.create_button("🚪 خروج", "exit")]
            ])
            await self.application.bot.send_message(
                chat_id,
                "🎉 به ربات مدیریت عادت‌های شخصی خوش اومدی!\n\n" +
                "✨ اینجا می‌تونی عادت‌هات رو ثبت کنی و پیشرفتت رو ببینی\n" +
                "🏆 امتیاز جمع کنی و تو چالش‌ها شرکت کنی\n\n" +
                "🎮 چی کار می‌خوای انجام بدی؟",
                reply_markup=keyboard
            )
        else:
            await self.show_main_menu(chat_id, user_id)

    # 📝 ثبت نام
    async def handle_registration(self, chat_id, user_id):
        self.set_user_state(user_id, "register_name")
        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_start")]
        ])
        await self.application.bot.send_message(
            chat_id,
            "✨ عالیه! بریم شروع کنیم\n\n" +
            "🎯 اسمت رو بگو تا بتونم صمیمی‌تر باهات حرف بزنم:",
            reply_markup=keyboard
        )

    async def handle_name_registration(self, chat_id, user_id, name):
        user_data = self.get_user_data(user_id)
        user_data["name"] = name
        self.set_user_state(user_id, "add_habits")
        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_start")]
        ])
        await self.application.bot.send_message(
            chat_id,
            f"🎉 سلام {name} عزیز!\n\n" +
            "🌱 حالا عادت‌هایی که می‌خوای روشون کار کنی رو بگو\n" +
            '📝 هر عادت رو تو یک خط بنویس (برای تموم کردن بنویس "تموم"):\n\n' +
            "مثال:\n" +
            "ورزش\n" +
            "مطالعه\n" +
            "آب خوردن",
            reply_markup=keyboard
        )

    async def handle_add_habits(self, chat_id, user_id, text):
        user_data = self.get_user_data(user_id)

        if text.lower() == "تموم":
            self.set_user_state(user_id, "main")
            message = (
                f"🎊 فوق‌العاده {user_data['name']}!\n\n" +
                "✅ عادت‌هات با موفقیت ثبت شدن:\n" +
                "\n".join(f"{i+1}. {h['name']}" for i, h in enumerate(user_data["habits"])) +
                "\n\n🚀 حالا آماده‌ای که شروع کنی!"
            ) if user_data["habits"] else "🤔 هیچ عادتی اضافه نکردی!"
            await self.application.bot.send_message(chat_id, message)
            await self.show_main_menu(chat_id, user_id)
            return

        habits = [h.strip() for h in text.split("\n") if h.strip()]
        if self.get_user_state(user_id) == "add_habits":
            user_data["habits"].extend({"name": habit, "id": time.time() + random.random()} for habit in habits)
        else:
            user_data["habits"].extend({"name": habit, "id": time.time() + random.random()} for habit in habits)


        await self.application.bot.send_message(
            chat_id,
            '📝 عادت بعدی رو بنویس یا بنویس "تموم":'
        )

    # 🏠 منوی اصلی
    async def show_main_menu(self, chat_id, user_id):
        self.set_user_state(user_id, "main")
        user_data = self.get_user_data(user_id)
        keyboard = self.create_inline_keyboard([
            [self.create_button("📊 گزارش روزانه", "daily_report")],
            [self.create_button("⚙️ ویرایش اطلاعات", "edit_info"), self.create_button("🎯 ویرایش عادت‌ها", "edit_habits")],
            [self.create_button("🏆 امتیاز", "score"), self.create_button("🔥 چالش", "challenge")],
            [self.create_button("👑 ادمین", "admin"), self.create_button("🚪 خروج", "exit")]
        ])
        await self.application.bot.send_message(
            chat_id,
            f"🌟 سلام {user_data['name']} عزیز!\n\n" +
            f"📈 امتیاز فعلی: {user_data['score']}\n" +
            f"📅 روز {self.calculate_user_day(user_data)}\n" +
            f"🎯 {len(user_data['habits'])} عادت فعال\n\n" +
            "🎮 چی کار می‌خوای بکنی؟",
            reply_markup=keyboard
        )

    # 📊 گزارش روزانه
    async def show_daily_report(self, chat_id, user_id):
        user_data = self.get_user_data(user_id)
        today = datetime.now().strftime("%Y-%m-%d")

        if today in user_data["daily_reports"] and user_data["daily_reports"][today].get("type") != "none":
            await self.application.bot.send_message(
                chat_id,
                "✅ گزارش امروزت رو قبلاً ثبت کردی!"
            )
            await self.show_main_menu(chat_id, user_id)
            return

        if not user_data["habits"]:
            await self.application.bot.send_message(
                chat_id,
                "🤔 هنوز عادتی ثبت نکردی!"
            )
            await self.show_main_menu(chat_id, user_id)
            return
        
        user_data['report_temp'] = {habit['id']: False for habit in user_data['habits']}

        buttons = self.get_report_buttons(user_id)
        keyboard = self.create_inline_keyboard(buttons)
        
        message_text = (
            f"📊 گزارش روزانه - روز {self.calculate_user_day(user_data)}\n\n" +
            "🎯 روی عادت‌هایی که انجام دادی، بزن:"
        )

        await self.application.bot.send_message(
            chat_id,
            message_text,
            reply_markup=keyboard
        )

    def get_report_buttons(self, user_id):
        user_data = self.get_user_data(user_id)
        buttons = []
        for habit in user_data["habits"]:
            status_emoji = "🟢" if user_data.get('report_temp', {}).get(habit['id']) else "⚪"
            buttons.append([self.create_button(f"{status_emoji} {habit['name']}", f"toggle_habit_report_{habit['id']}")])
        
        buttons.append([self.create_button("✅ ثبت گزارش", "submit_daily_report")])
        buttons.append([self.create_button("💤 استراحت", "report_rest")])
        buttons.append([self.create_button("🔙 بازگشت", "back_to_main")])
        return buttons
        
    async def handle_submit_daily_report(self, chat_id, user_id):
        user_data = self.get_user_data(user_id)
        today = datetime.now().strftime("%Y-%m-%d")
        
        done_habits = [habit for habit in user_data['habits'] if user_data.get('report_temp', {}).get(habit['id'])]
        done_habits_ids = [habit['id'] for habit in done_habits]
        total_habits = len(user_data['habits'])
        
        score_change = 0
        report_type = "none"
        message_text = ""
        group_message = ""
        
        
        # Check if the user had a 'none' report today
        initial_report_was_none = today in user_data["daily_reports"] and user_data["daily_reports"][today].get("type") == "none"
        
        # if user had a 'none' report, we should first undo the score change
        if initial_report_was_none:
            user_data["score"] += 10
        
        if len(done_habits) == total_habits:
            score_change = 10
            report_type = "complete"
            message_text = "همه عادت‌هات رو کامل انجام دادی"
            group_message = (
                f"گزارش کار عالیه ({user_data['name']})\n"
                f"ایدی: @{user_data['username']}\n\n"
                + "\n".join([h['name'] for h in done_habits]) +
                "\n\nآفرین! همه عادت‌ها رو کامل کردی! 💪 🟢"
            )
        elif len(done_habits) > 0:
            score_change = 5
            report_type = "partial"
            message_text = "ناقص انجام دادی"
            group_message = (
                f"گزارش کار {user_data['name']}\n"
                f"ایدی: @{user_data['username']}\n\n"
                + "\n".join([h['name'] for h in done_habits]) +
                f"\n\n5 دقیقه برای اون {len(user_data['habits']) - len(done_habits)} عادتت وقت بزار و کاملش کن تا شب 😅 🟡"
            )
        else:
            score_change = -10
            report_type = "none"
            message_text = "هیچ عادتی رو انجام ندادی"
            group_message = (
                f"گزارش کار {user_data['name']}\n"
                f"ایدی: @{user_data['username']}\n\n"
                "هیچ عادتی انجام نشده\n\n"
                "هیچ کاری انجام نشد! 😅 برو یه تلاشی بده! 🔴"
            )
            
        # Update the score
        user_data["score"] += score_change

        user_data["daily_reports"][today] = {
            "type": report_type, 
            "score_change": score_change, 
            "date": datetime.now(),
            "completed_habits": done_habits_ids
        }
        user_data.pop('report_temp', None)
        
        new_score = user_data["score"]
        day_num = self.calculate_user_day(user_data)

        # Send a message to the group
        await self.application.bot.send_message(
            self.GROUP_CHAT_ID,
            group_message
        )
        
        # Send a message to the user
        await self.application.bot.send_message(
            chat_id,
            f"🎉 گزارش روزانه‌ات ثبت شد!\n\n" +
            f"💬 {message_text}\n" +
            f"📈 امتیاز: {('+' if score_change > 0 else '')}{score_change}\n" +
            f"🏆 مجموع امتیاز: {new_score}\n" +
            f"📅 روز {day_num}\n\n" +
            f"{self.get_motivational_message(report_type)}"
        )
        await self.check_challenge_status(user_id, chat_id)
        await self.show_main_menu(chat_id, user_id)

    def get_motivational_message(self, report_type):
        messages = {
            "complete": ["🔥 عالی بودی!", "💪 همینطور ادامه بده!", "⭐ فوق‌العاده‌ای!"],
            "partial": ["👍 خوب بود، دفعه بعد بهتر!", "💯 داری پیشرفت می‌کنی!", "🎯 نزدیک هدف هستی!"],
            "none": ["😔 مشکلی نیست، فردا شروع تازه!", "💪 از امروز شروع کن!", "🌅 هر روز فرصت تازه‌ای هست!"],
            "rest": ["😴 استراحت هم لازمه!", "🧘‍♂️ آرامش مهمه!", "💤 خوب استراحت کردی!"]
        }
        return random.choice(messages.get(report_type, messages["complete"]))

    # ⚙️ ویرایش اطلاعات
    async def show_edit_info(self, chat_id, user_id):
        keyboard = self.create_inline_keyboard([
            [self.create_button("📝 تغییر نام", "change_name")],
            [self.create_button("🔙 بازگشت", "back_to_main")]
        ])
        await self.application.bot.send_message(
            chat_id,
            "⚙️ ویرایش اطلاعات شخصی\n\n" +
            "🎨 چی رو می‌خوای تغییر بدی؟",
            reply_markup=keyboard
        )

    async def handle_change_name(self, chat_id, user_id):
        self.set_user_state(user_id, "change_name")
        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_edit_info")]
        ])
        await self.application.bot.send_message(
            chat_id,
            "✨ نام جدیدت رو بگو:",
            reply_markup=keyboard
        )

    async def handle_change_name_input(self, chat_id, user_id, name):
        user_data = self.get_user_data(user_id)
        user_data["name"] = name
        self.set_user_state(user_id, "main")
        await self.application.bot.send_message(
            chat_id,
            f"✅ نامت به \"{name}\" تغییر کرد!"
        )
        await self.show_main_menu(chat_id, user_id)

    # 🎯 ویرایش عادت‌ها
    async def show_edit_habits(self, chat_id, user_id):
        self.set_user_state(user_id, "edit_habits")
        keyboard = self.create_inline_keyboard([
            [self.create_button("➕ اضافه عادت", "add_habit")],
            [self.create_button("✏️ ویرایش عادت", "edit_habit")],
            [self.create_button("🗑️ حذف عادت", "delete_habit")],
            [self.create_button("🔙 بازگشت", "back_to_main")]
        ])
        await self.application.bot.send_message(
            chat_id,
            "🎯 مدیریت عادت‌ها\n\n" +
            "🔧 چی کار می‌خوای بکنی؟",
            reply_markup=keyboard
        )

    async def show_add_habit(self, chat_id, user_id):
        self.set_user_state(user_id, "add_habits_new")
        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_edit_habits")]
        ])
        await self.application.bot.send_message(
            chat_id,
            "➕ اضافه کردن عادت جدید\n\n" +
            '📝 عادت‌های جدیدت رو خط به خط بنویس (برای تموم کردن بنویس "تموم"):\n\n' +
            "مثال:\n" +
            "ریاضی\n" +
            "ماشین",
            reply_markup=keyboard
        )

    async def show_habits_for_action(self, chat_id, user_id, action):
        user_data = self.get_user_data(user_id)

        if not user_data["habits"]:
            await self.application.bot.send_message(
                chat_id,
                "🤷‍♂️ هیچ عادتی ثبت نکردی!\n\n" +
                "➕ اول برو عادت اضافه کن"
            )
            await self.show_edit_habits(chat_id, user_id)
            return

        action_text = "حذف" if action == "delete" else "ویرایش"
        action_emoji = "🗑️" if action == "delete" else "✏️"
        buttons = [
            [self.create_button(f"{i+1}. {habit['name']}", f"{action}_habit_{i}")]
            for i, habit in enumerate(user_data["habits"])
        ]
        buttons.append([self.create_button("🔙 بازگشت", "back_to_edit_habits")])
        keyboard = self.create_inline_keyboard(buttons)

        await self.application.bot.send_message(
            chat_id,
            f"{action_emoji} {action_text} عادت\n\n" +
            f"📋 لطفاً شماره عادتی که می‌خواهید {action_text} شود را انتخاب کنید:\n\n" +
            "\n".join(f"{i+1}. {h['name']}" for i, h in enumerate(user_data["habits"])),
            reply_markup=keyboard
        )

    async def handle_edit_habit(self, chat_id, user_id, text):
        user_data = self.get_user_data(user_id)
        try:
            index = int(text) - 1
            if index < 0 or index >= len(user_data["habits"]):
                await self.application.bot.send_message(
                    chat_id,
                    "❌ شماره عادت نامعتبره! دوباره امتحان کن یا بنویس \"بازگشت\""
                )
                return
            user_data["habits"][index]["name"] = text
            self.set_user_state(user_id, "main")
            await self.application.bot.send_message(
                chat_id,
                f"✏️ عادت به \"{text}\" تغییر کرد!\n\n" +
                "📋 لیست عادت‌های فعلی:\n" +
                "\n".join(f"{i+1}. {h['name']}" for i, h in enumerate(user_data["habits"]))
            )
            await self.show_edit_habits(chat_id, user_id)
        except ValueError:
            if text.lower() == "بازگشت":
                await self.show_edit_habits(chat_id, user_id)
            else:
                await self.application.bot.send_message(
                    chat_id,
                    "❌ لطفاً یک شماره معتبر وارد کنید یا بنویس \"بازگشت\""
                )

    async def handle_habit_deletion(self, chat_id, user_id, habit_index):
        user_data = self.get_user_data(user_id)
        deleted_habit = user_data["habits"].pop(habit_index)
        await self.application.bot.send_message(
            chat_id,
            f"🗑️ عادت \"{deleted_habit['name']}\" حذف شد!\n\n" +
            "📋 لیست عادت‌های فعلی:\n" +
            ("\n".join(f"{i+1}. {h['name']}" for i, h in enumerate(user_data["habits"]))
             if user_data["habits"] else "🈳 هیچ عادتی ثبت نشده")
        )
        await self.show_edit_habits(chat_id, user_id)

    # 🏆 امتیاز
    async def show_score(self, chat_id, user_id):
        user_data = self.get_user_data(user_id)
        day_num = self.calculate_user_day(user_data)
        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_main")]
        ])
        await self.application.bot.send_message(
            chat_id,
            f"🏆 امتیاز {user_data['name']}\n\n" +
            f"💎 امتیاز فعلی: {user_data['score']}\n" +
            f"📅 روز فعالیت: {day_num}\n" +
            f"📈 میانگین امتیاز: {user_data['score'] / day_num:.1f}\n\n" +
            f"{self.get_score_message(user_data['score'])}",
            reply_markup=keyboard
        )

    def get_score_message(self, score):
        if score >= 100:
            return "👑 قهرمان هستی!"
        elif score >= 50:
            return "🔥 داری عالی پیش میری!"
        elif score >= 0:
            return "💪 ادامه بده!"
        return "🌱 از همین الان شروع کن!"

    # 🔥 چالش
    async def show_challenge(self, chat_id, user_id):
        if not self.challenges:
            keyboard = self.create_inline_keyboard([
                [self.create_button("🔙 بازگشت", "back_to_main")]
            ])
            await self.application.bot.send_message(
                chat_id,
                "🤷‍♂️ در حال حاضر چالشی فعال نیست!\n\n" +
                "⏳ منتظر چالش‌های جدید باش!",
                reply_markup=keyboard
            )
            return

        user_data = self.get_user_data(user_id)
        current_challenge = self.challenges[0]

        if not user_data["challenge_status"]:
            keyboard = self.create_inline_keyboard([
                [self.create_button("✅ آره", "join_challenge")],
                [self.create_button("❌ نه", "decline_challenge")],
                [self.create_button("🔙 بازگشت", "back_to_main")]
            ])
            await self.application.bot.send_message(
                chat_id,
                f"🔥 چالش فعال: {current_challenge['text']}\n\n" +
                f"🎯 هدف: رسیدن به {current_challenge['target_score']} امتیاز\n" +
                f"⏱️ مدت: {current_challenge['duration']} روز\n\n" +
                "🤔 آیا در چالش شرکت می‌کنی؟",
                reply_markup=keyboard
            )
        else:
            await self.show_challenge_status(chat_id, user_id, current_challenge)

    async def show_challenge_status(self, chat_id, user_id, challenge):
        user_data = self.get_user_data(user_id)
        days_elapsed = (datetime.now() - user_data["challenge_status"]["join_date"]).days
        remaining_days = challenge["duration"] - days_elapsed
        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_main")]
        ])
        status_emoji = "🏆" if user_data["score"] >= challenge["target_score"] else "💪"
        status_text = "موفق شدی!" if user_data["score"] >= challenge["target_score"] else "ادامه بده!"
        await self.application.bot.send_message(
            chat_id,
            f"🔥 چالش: {challenge['text']}\n\n" +
            f"📅 روز ({days_elapsed}/{challenge['duration']})\n" +
            f"🏆 امتیاز ({user_data['score']}/{challenge['target_score']})\n" +
            f"⏳ {remaining_days} روز باقی مونده\n\n" +
            f"{status_emoji} {status_text}",
            reply_markup=keyboard
        )

    async def check_challenge_status(self, user_id, chat_id):
        user_data = self.get_user_data(user_id)
        if not user_data["challenge_status"] or not self.challenges:
            return

        challenge = self.challenges[0]
        if user_data["score"] >= challenge["target_score"]:
            await self.application.bot.send_message(
                self.GROUP_CHAT_ID,
                f"🎉 تبریک! {user_data['name']} در چالش \"{challenge['text']}\" موفق شد! 🏆"
            )
            user_data["challenge_status"] = None

    # 👑 پنل ادمین
    async def show_admin_login(self, chat_id, user_id):
        self.set_user_state(user_id, "admin_password")
        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_start")]
        ])
        await self.application.bot.send_message(
            chat_id,
            "👑 ورود ادمین\n\n" +
            "🔐 رمز ادمین را وارد کنید:",
            reply_markup=keyboard
        )

    async def handle_admin_password(self, chat_id, user_id, password):
        if password != self.ADMIN_PASSWORD:
            await self.application.bot.send_message(
                chat_id,
                "❌ رمز اشتباه است!\n\n" +
                "🔒 دوباره تلاش کنید"
            )
            return
        self.set_user_state(user_id, "admin_main")
        await self.show_admin_panel(chat_id, user_id)

    async def show_admin_panel(self, chat_id, user_id):
        keyboard = self.create_inline_keyboard([
            [self.create_button("🗑️ ریست کل", "admin_reset_all")],
            [self.create_button("👤 حذف کاربر خاص", "admin_reset_user")],
            [self.create_button("🔥 ایجاد چالش", "admin_create_challenge")],
            [self.create_button("📊 گزارش کاربران", "admin_user_report")],
            [self.create_button("🏆 جدول امتیازات", "admin_scoreboard")],
            [self.create_button("🔙 بازگشت", "back_to_start")]
        ])
        await self.application.bot.send_message(
            chat_id,
            "👑 پنل مدیریت\n\n" +
            "🎮 چه کاری می‌خوای انجام بدی؟",
            reply_markup=keyboard
        )

    async def handle_reset_all(self, chat_id, user_id):
        self.users.clear()
        self.challenges.clear()
        self.user_states.clear()
        await self.application.bot.send_message(
            chat_id,
            "🗑️ همه داده‌ها با موفقیت ریست شدند!"
        )
        await self.show_admin_panel(chat_id, user_id)

    async def show_reset_user(self, chat_id, user_id):
        buttons = [
            [self.create_button(f"{i+1}. {user_data['name']}", f"delete_user_{u_id}")]
            for i, (u_id, user_data) in enumerate(self.users.items())
        ]
        buttons.append([self.create_button("🔙 بازگشت", "back_to_admin")])
        keyboard = self.create_inline_keyboard(buttons)
        await self.application.bot.send_message(
            chat_id,
            "👤 حذف کاربر خاص\n\n" +
            "📋 لطفاً کاربر موردنظر را انتخاب کنید:\n\n" +
            "\n".join(f"{i+1}. {u['name']}" for i, u in enumerate(self.users.values())),
            reply_markup=keyboard
        )

    async def handle_reset_user(self, chat_id, user_id, target_user_id):
        user_data = self.users.get(target_user_id)
        if user_data:
            del self.users[target_user_id]
            self.user_states.pop(target_user_id, None)
            await self.application.bot.send_message(
                chat_id,
                f"🗑️ کاربر {user_data['name']} با موفقیت حذف شد!"
            )
        await self.show_admin_panel(chat_id, user_id)

    async def show_user_report(self, chat_id, user_id):
        today = datetime.now().strftime("%Y-%m-%d")
        report = "📊 گزارش امروز کاربران:\n\n"
        for u_id, user_data in self.users.items():
            day_num = self.calculate_user_day(user_data)
            today_report = user_data["daily_reports"].get(today)
            status = "⏳ گزارش نداده"
            score_change = -10
            incomplete_habits = []

            if today_report:
                if today_report["type"] == "complete":
                    status = "🟢 کامل انجام داد"
                    score_change = 10
                elif today_report["type"] == "partial":
                    status = "🟡 ناقص انجام داد"
                    score_change = 5
                    completed_ids = today_report.get("completed_habits", [])
                    incomplete_habits = [h['name'] for h in user_data["habits"] if h['id'] not in completed_ids]
                elif today_report["type"] == "none":
                    status = "🔴 انجام نداد"
                    score_change = -10
                    incomplete_habits = [h['name'] for h in user_data["habits"]]
                elif today_report["type"] == "rest":
                    status = "😴 استراحت کرد"
                    score_change = 0
            else:
                user_data["score"] -= 10
                incomplete_habits = [h['name'] for h in user_data["habits"]]
                user_data["daily_reports"][today] = {"type": "none", "score_change": -10, "date": datetime.now(), "completed_habits": []}


            report += f"👤 {user_data['name']} - روز {day_num}\n"
            report += f"{status} (امتیاز: {('+' if score_change > 0 else '')}{score_change})\n"
            if incomplete_habits:
                report += f"⚠️ عادت‌های انجام‌نشده: {', '.join(incomplete_habits)}\n"
            report += "--------------------\n"

        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_admin")]
        ])
        await self.application.bot.send_message(chat_id, report, reply_markup=keyboard)

    async def show_scoreboard(self, chat_id, user_id):
        sorted_users = sorted(self.users.items(), key=lambda x: x[1]["score"], reverse=True)
        scoreboard = "🏆 جدول امتیازات\n\n"
        for i, (u_id, user_data) in enumerate(sorted_users):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🏅"
            scoreboard += f"{medal} {user_data['name']}: {user_data['score']}\n"
        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_admin")]
        ])
        await self.application.bot.send_message(chat_id, scoreboard, reply_markup=keyboard)

    # 🔥 مدیریت چالش
    async def show_create_challenge(self, chat_id, user_id):
        self.set_user_state(user_id, "challenge_text")
        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_admin")]
        ])
        await self.application.bot.send_message(
            chat_id,
            "🔥 ایجاد چالش جدید\n\n" +
            "📝 متن چالش رو بنویس:",
            reply_markup=keyboard
        )

    async def handle_challenge_text(self, chat_id, user_id, text):
        self.temp_challenge = {"text": text}
        self.set_user_state(user_id, "challenge_duration")
        keyboard = self.create_inline_keyboard([
            [self.create_button("🔙 بازگشت", "back_to_admin")]
        ])
        await self.application.bot.send_message(
            chat_id,
            "⏱️ مدت چالش رو بگو (به روز):\n\n" +
            "مثال: 30",
            reply_markup=keyboard
        )

    async def handle_challenge_duration(self, chat_id, user_id, text):
        try:
            duration = int(text)
            if duration <= 0:
                await self.application.bot.send_message(
                    chat_id,
                    "❌ لطفاً یک عدد معتبر وارد کنید"
                )
                return
            self.temp_challenge["duration"] = duration
            self.set_user_state(user_id, "challenge_target")
            keyboard = self.create_inline_keyboard([
                [self.create_button("🔙 بازگشت", "back_to_admin")]
            ])
            await self.application.bot.send_message(
                chat_id,
                "🎯 امتیاز هدف رو بگو:\n\n" +
                "مثال: 100",
                reply_markup=keyboard
            )
        except ValueError:
            await self.application.bot.send_message(
                chat_id,
                "❌ لطفاً یک عدد معتبر وارد کنید"
            )

    async def handle_challenge_target(self, chat_id, user_id, text):
        try:
            target_score = int(text)
            if target_score <= 0:
                await self.application.bot.send_message(
                    chat_id,
                    "❌ لطفاً یک عدد معتبر وارد کنید"
                )
                return
            self.temp_challenge["target_score"] = target_score
            self.temp_challenge["created_at"] = datetime.now()
            self.challenges = [self.temp_challenge]
            self.temp_challenge = None
            self.set_user_state(user_id, "admin_main")
            await self.application.bot.send_message(
                chat_id,
                "🎉 چالش با موفقیت ایجاد شد! کاربران می‌تونن از حالا ثبت‌نام کنن."
            )
            await self.show_admin_panel(chat_id, user_id)
        except ValueError:
            await self.application.bot.send_message(
                chat_id,
                "❌ لطفاً یک عدد معتبر وارد کنید"
            )

    # 🎮 مدیریت Callback Query
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = query.message.chat_id
        user_id = query.from_user.id
        data = query.data

        await query.answer()
        
        user_data = self.get_user_data(user_id)
        if query.from_user.username:
            user_data['username'] = query.from_user.username

        if data == "register":
            await self.handle_registration(chat_id, user_id)
        elif data == "admin":
            await self.show_admin_login(chat_id, user_id)
        elif data == "exit":
            await self.application.bot.send_message(chat_id, "🚪 خداحافظ! هر وقت خواستی برگرد 😊")
        elif data == "back_to_start":
            await self.show_start_menu(update, context)
        elif data == "daily_report":
            await self.show_daily_report(chat_id, user_id)
        elif data == "edit_info":
            await self.show_edit_info(chat_id, user_id)
        elif data == "edit_habits":
            await self.show_edit_habits(chat_id, user_id)
        elif data == "score":
            await self.show_score(chat_id, user_id)
        elif data == "challenge":
            await self.show_challenge(chat_id, user_id)
        elif data == "join_challenge":
            user_data = self.get_user_data(user_id)
            user_data["challenge_status"] = {"join_date": datetime.now()}
            await self.application.bot.send_message(chat_id, "🎉 با موفقیت وارد چالش شدی!")
            await self.show_challenge_status(chat_id, user_id, self.challenges[0])
        elif data == "decline_challenge":
            await self.show_main_menu(chat_id, user_id)
        elif data == "back_to_main":
            await self.show_main_menu(chat_id, user_id)
        elif data == "change_name":
            await self.handle_change_name(chat_id, user_id)
        elif data == "back_to_edit_info":
            await self.show_edit_info(chat_id, user_id)
        elif data == "add_habit":
            await self.show_add_habit(chat_id, user_id)
        elif data == "edit_habit":
            self.set_user_state(user_id, "edit_habit")
            await self.show_habits_for_action(chat_id, user_id, "edit")
        elif data == "delete_habit":
            await self.show_habits_for_action(chat_id, user_id, "delete")
        elif data == "back_to_edit_habits":
            await self.show_edit_habits(chat_id, user_id)
        elif data == "report_rest":
            await self.handle_daily_report_rest(chat_id, user_id)
        elif data.startswith("toggle_habit_report_"):
            habit_id = float(data.split("_")[3])
            user_data = self.get_user_data(user_id)
            user_data['report_temp'][habit_id] = not user_data['report_temp'].get(habit_id, False)

            await query.edit_message_text(
                text=query.message.text,
                reply_markup=self.create_inline_keyboard(self.get_report_buttons(user_id))
            )
        elif data == "submit_daily_report":
            await self.handle_submit_daily_report(chat_id, user_id)
        elif data == "admin_reset_all":
            await self.handle_reset_all(chat_id, user_id)
        elif data == "admin_reset_user":
            await self.show_reset_user(chat_id, user_id)
        elif data == "admin_create_challenge":
            await self.show_create_challenge(chat_id, user_id)
        elif data == "admin_user_report":
            await self.show_user_report(chat_id, user_id)
        elif data == "admin_scoreboard":
            await self.show_scoreboard(chat_id, user_id)
        elif data == "back_to_admin":
            await self.show_admin_panel(chat_id, user_id)
        elif data.startswith("delete_habit_"):
            index = int(data.split("_")[2])
            await self.handle_habit_deletion(chat_id, user_id, index)
        elif data.startswith("edit_habit_"):
            self.set_user_state(user_id, "edit_habit")
            await self.application.bot.send_message(chat_id, "✏️ نام جدید عادت رو بنویس:")
        elif data.startswith("delete_user_"):
            target_user_id = int(data.split("_")[2])
            await self.handle_reset_user(chat_id, user_id, target_user_id)

    async def handle_daily_report_rest(self, chat_id, user_id):
        user_data = self.get_user_data(user_id)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if the user had a 'none' report today
        initial_report_was_none = today in user_data["daily_reports"] and user_data["daily_reports"][today].get("type") == "none"

        score_change = 0
        report_type = "rest"
        
        if initial_report_was_none:
            user_data["score"] += 10 # Undo the -10 from daily check
            
        user_data["daily_reports"][today] = {
            "type": report_type, 
            "score_change": score_change, 
            "date": datetime.now(),
            "completed_habits": []
        }
        user_data.pop('report_temp', None)

        await self.application.bot.send_message(
            self.GROUP_CHAT_ID,
            f"گزارش کار {user_data['name']}\n"
            f"ایدی: @{user_data['username']}\n\n"
            "امروز استراحت کرد! 💤"
        )
        
        await self.application.bot.send_message(
            chat_id,
            f"✅ گزارش روزانه‌ات ثبت شد! روز استراحت خوبی داشته باشی. 😌"
        )
        await self.show_main_menu(chat_id, user_id)

    # ⏰ بررسی روزانه
    def schedule_daily_check(self):
        async def check():
            today = datetime.now().strftime("%Y-%m-%d")
            for u_id, user_data in self.users.items():
                if today not in user_data["daily_reports"]:
                    user_data["score"] -= 10
                    user_data["daily_reports"][today] = {
                        "type": "none", 
                        "score_change": -10, 
                        "date": datetime.now(),
                        "completed_habits": []
                    }
            
            # This part might need adjustment if you want to send a report to the group chat
            # For now, it's just updating user data.
            # If you want to send a report, you'd need to call a method like show_user_report
            # and pass the correct chat_id (self.GROUP_CHAT_ID) and a dummy user_id or handle it differently.
            pass # Placeholder for potential group report logic


        def run_schedule():
            schedule.every().day.at("00:00").do(lambda: asyncio.run_coroutine_threadsafe(check(), self.application.loop))
            while True:
                schedule.run_pending()
                time.sleep(60)

        threading.Thread(target=run_schedule, daemon=True).start()

    def run(self):
        self.application.run_polling()

if __name__ == "__main__":
    bot = HabitTrackerBot(os.getenv("TELEGRAM_TOKEN"), os.getenv("GROUP_CHAT_ID"))
    while True:
        try:
            bot.run()
        except Exception as e:
            logger.error(f"Error in polling: {e}")
            time.sleep(10)
