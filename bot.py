from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import re

TOKEN = "8259659828:AAFQP0Rnmf12VFdOkjyDdyXVFY_VwmgXtzE"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

group_settings = {}

default_filtered_words = {"بد", "زشت", "هرز"}

auto_responses = {}

default_settings = {
    "filter_link": True,
    "filter_word": True,
    "auto_respond": True
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات مدیریت گروه فعال شد.")

def get_group_settings(chat_id):
    if chat_id not in group_settings:
        group_settings[chat_id] = {
            "filter_link": default_settings["filter_link"],
            "filter_word": default_settings["filter_word"],
            "auto_respond": default_settings["auto_respond"],
            "filtered_words": set(default_filtered_words),
            "auto_responses": dict(auto_responses)
        }
    return group_settings[chat_id]

async def toggle_feature(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not update.effective_chat.get_member(user.id).status in ["administrator", "creator"]:
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return

    args = context.args
    if len(args) != 2:
        await update.message.reply_text("فرمت دستور اشتباه است. مثلاً: /filterlink on یا /filterlink off")
        return

    feature = args[0].lower()
    action = args[1].lower()

    settings = get_group_settings(chat_id)

    if feature not in ["filterlink", "filterword", "autorespond"]:
        await update.message.reply_text("این قابلیت وجود ندارد. قابلیت‌ها: filterlink, filterword, autorespond")
        return

    if action == "on":
        settings[feature] = True
        await update.message.reply_text(f"قابلیت {feature} روشن شد.")
    elif action == "off":
        settings[feature] = False
        await update.message.reply_text(f"قابلیت {feature} خاموش شد.")
    else:
        await update.message.reply_text("عملیات نامعتبر است. فقط on یا off قبول است.")

async def add_filtered_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not update.effective_chat.get_member(user.id).status in ["administrator", "creator"]:
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return

    if not context.args:
        await update.message.reply_text("لطفاً کلمه‌ای برای فیلتر شدن وارد کنید. مثلاً: /addword بد")
        return

    word = context.args[0]
    settings = get_group_settings(chat_id)
    settings["filtered_words"].add(word)
    await update.message.reply_text(f"کلمه «{word}» به لیست فیلتر اضافه شد.")

async def remove_filtered_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not update.effective_chat.get_member(user.id).status in ["administrator", "creator"]:
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return

    if not context.args:
        await update.message.reply_text("لطفاً کلمه‌ای برای حذف از فیلتر وارد کنید. مثلاً: /removeword بد")
        return

    word = context.args[0]
    settings = get_group_settings(chat_id)
    if word in settings["filtered_words"]:
        settings["filtered_words"].remove(word)
        await update.message.reply_text(f"کلمه «{word}» از لیست فیلتر حذف شد.")
    else:
        await update.message.reply_text(f"کلمه «{word}» در لیست فیلتر نبود.")

async def add_auto_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not update.effective_chat.get_member(user.id).status in ["administrator", "creator"]:
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return

    if not context.args:
        await update.message.reply_text("لطفاً کلمه‌ای برای پاسخ خودکار وارد کنید. مثلاً: /addresponse ترامینا")
        return

    word = context.args[0]
    settings = get_group_settings(chat_id)

    settings["waiting_for_response"] = word
    await update.message.reply_text(f"لطفاً پاسخ خودکار برای کلمه «{word}» را ارسال کنید.")

async def receive_auto_response_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    settings = get_group_settings(chat_id)

    if "waiting_for_response" in settings:
        word = settings["waiting_for_response"]
        text = update.message.text or ""
        settings["auto_responses"][word] = text
        del settings["waiting_for_response"]
        await update.message.reply_text(f"پاسخ خودکار برای کلمه «{word}» تنظیم شد.")

async def remove_auto_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not update.effective_chat.get_member(user.id).status in ["administrator", "creator"]:
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return

    if not context.args:
        await update.message.reply_text("لطفاً کلمه‌ای برای حذف پاسخ خودکار وارد کنید. مثلاً: /removeresponse ترامینا")
        return

    word = context.args[0]
    settings = get_group_settings(chat_id)
    if word in settings["auto_responses"]:
        del settings["auto_responses"][word]
        await update.message.reply_text(f"پاسخ خودکار برای کلمه «{word}» حذف شد.")
    else:
        await update.message.reply_text(f"کلمه «{word}» پاسخ خودکار نداشت.")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = update.effective_chat.id
    text = message.text or ""
    settings = get_group_settings(chat_id)

    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    if settings["filter_link"]:
        if re.search(r"https?://", text):
            try:
                await message.delete()
                await update.message.reply_text(f"پیام حاوی لینک حذف شد.")
            except:
                pass
            return

    if settings["filter_word"]:
        for w in settings["filtered_words"]:
            if w in text:
                try:
                    await message.delete()
                    await update.message.reply_text(f"پیام حاوی کلمه فیلتر شده حذف شد.")
                except:
                    pass
                return

    if settings["auto_respond"]:
        for w, resp in settings["auto_responses"].items():
            if w in text:
                await update.message.reply_text(resp)
                return

async def del_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not update.effective_chat.get_member(user.id).status in ["administrator", "creator"]:
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return

    args = context.args
    if len(args) != 1 or not args[0].isdigit():
        await update.message.reply_text("لطفاً تعداد پیام‌های قابل حذف را وارد کنید. مثلاً: /del 5")
        return

    count = int(args[0])
    msgs = []
    async for msg in context.bot.get_chat(chat_id).iter_history(limit=count + 1):
        msgs.append(msg)

    for m in msgs:
        try:
            await m.delete()
        except:
            pass
    await update.message.reply_text(f"{count} پیام آخر حذف شد.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["filterlink", "filterword", "autorespond"], toggle_feature))
    app.add_handler(CommandHandler("addword", add_filtered_word))
    app.add_handler(CommandHandler("removeword", remove_filtered_word))
    app.add_handler(CommandHandler("addresponse", add_auto_response))
    app.add_handler(CommandHandler("removeresponse", remove_auto_response))
    app.add_handler(CommandHandler("del", del_messages))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), receive_auto_response_message))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))

    await app.run_polling()

import asyncio
asyncio.run(main())
