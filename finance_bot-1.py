"""
بوت تمويل وهمي على تلغرام
Virtual Finance Bot for Telegram
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ✅ ضع التوكن هنا
BOT_TOKEN = "ضع_توكن_البوت_هنا"

# قاعدة بيانات المستخدمين (في الذاكرة - مؤقتة)
users_db = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────
# دوال مساعدة
# ─────────────────────────────────────────

def get_user(user_id: int) -> dict:
    """إنشاء أو استرجاع بيانات المستخدم"""
    if user_id not in users_db:
        users_db[user_id] = {
            "balance": 10000.0,       # رصيد افتراضي
            "portfolio": {},           # الأسهم المملوكة
            "transactions": [],        # سجل العمليات
            "total_invested": 0.0,
        }
    return users_db[user_id]


def format_money(amount: float) -> str:
    return f"{amount:,.2f} $"


# أسعار وهمية للأسهم
STOCKS = {
    "AAPL": {"name": "Apple", "price": 189.50, "emoji": "🍎"},
    "GOOGL": {"name": "Google", "price": 141.80, "emoji": "🔍"},
    "TSLA": {"name": "Tesla", "price": 245.30, "emoji": "⚡"},
    "AMZN": {"name": "Amazon", "price": 178.60, "emoji": "📦"},
    "MSFT": {"name": "Microsoft", "price": 415.20, "emoji": "💻"},
    "META": {"name": "Meta", "price": 520.10, "emoji": "📘"},
    "NVDA": {"name": "NVIDIA", "price": 875.00, "emoji": "🖥️"},
    "BTC":  {"name": "Bitcoin", "price": 68000.0, "emoji": "₿"},
}

import random

def get_live_price(symbol: str) -> float:
    """محاكاة تغيير السعر عشوائياً"""
    base = STOCKS[symbol]["price"]
    change = random.uniform(-0.03, 0.03)  # ±3%
    return round(base * (1 + change), 2)


# ─────────────────────────────────────────
# الأوامر الأساسية
# ─────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user(user.id)  # إنشاء حساب

    keyboard = [
        [InlineKeyboardButton("💰 رصيدي", callback_data="balance"),
         InlineKeyboardButton("📊 الأسواق", callback_data="market")],
        [InlineKeyboardButton("🛒 شراء سهم", callback_data="buy_menu"),
         InlineKeyboardButton("💸 بيع سهم", callback_data="sell_menu")],
        [InlineKeyboardButton("📁 محفظتي", callback_data="portfolio"),
         InlineKeyboardButton("📜 سجل العمليات", callback_data="history")],
        [InlineKeyboardButton("🎁 مكافأة يومية", callback_data="bonus")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 أهلاً {user.first_name}!\n\n"
        "🏦 *بوت التمويل الوهمي*\n"
        "━━━━━━━━━━━━━━━\n"
        "💡 تعلّم الاستثمار بدون مخاطر حقيقية!\n"
        "رصيدك الابتدائي: *10,000.00 $*\n\n"
        "اختر من القائمة:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 رصيدي", callback_data="balance"),
         InlineKeyboardButton("📊 الأسواق", callback_data="market")],
        [InlineKeyboardButton("🛒 شراء سهم", callback_data="buy_menu"),
         InlineKeyboardButton("💸 بيع سهم", callback_data="sell_menu")],
        [InlineKeyboardButton("📁 محفظتي", callback_data="portfolio"),
         InlineKeyboardButton("📜 سجل العمليات", callback_data="history")],
        [InlineKeyboardButton("🎁 مكافأة يومية", callback_data="bonus")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📋 *القائمة الرئيسية:*", parse_mode="Markdown", reply_markup=reply_markup)


# ─────────────────────────────────────────
# معالج الأزرار
# ─────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    user = get_user(user_id)

    # ── الرصيد ──
    if data == "balance":
        portfolio_value = sum(
            get_live_price(sym) * qty
            for sym, qty in user["portfolio"].items()
        )
        total = user["balance"] + portfolio_value
        profit = total - 10000.0
        profit_emoji = "📈" if profit >= 0 else "📉"

        text = (
            "💰 *حسابك المالي*\n"
            "━━━━━━━━━━━━━━━\n"
            f"💵 النقود: `{format_money(user['balance'])}`\n"
            f"📊 قيمة المحفظة: `{format_money(portfolio_value)}`\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🏦 الإجمالي: `{format_money(total)}`\n"
            f"{profit_emoji} الربح/الخسارة: `{format_money(profit)}`"
        )
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # ── الأسواق ──
    elif data == "market":
        text = "📊 *أسعار السوق اللحظية*\n━━━━━━━━━━━━━━━\n"
        for sym, info in STOCKS.items():
            price = get_live_price(sym)
            text += f"{info['emoji']} {info['name']} (`{sym}`): `{format_money(price)}`\n"
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # ── شراء - قائمة ──
    elif data == "buy_menu":
        keyboard = [
            [InlineKeyboardButton(f"{info['emoji']} {sym}", callback_data=f"buy_{sym}")]
            for sym, info in STOCKS.items()
        ]
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
        await query.edit_message_text(
            "🛒 *اختر السهم للشراء:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ── شراء - اختيار كمية ──
    elif data.startswith("buy_"):
        sym = data.split("_")[1]
        price = get_live_price(sym)
        info = STOCKS[sym]
        keyboard = [
            [InlineKeyboardButton("1 سهم", callback_data=f"confirm_buy_{sym}_1"),
             InlineKeyboardButton("5 أسهم", callback_data=f"confirm_buy_{sym}_5")],
            [InlineKeyboardButton("10 أسهم", callback_data=f"confirm_buy_{sym}_10"),
             InlineKeyboardButton("50 سهم", callback_data=f"confirm_buy_{sym}_50")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="buy_menu")],
        ]
        await query.edit_message_text(
            f"{info['emoji']} *{info['name']}* (`{sym}`)\n"
            f"💲 السعر الحالي: `{format_money(price)}`\n\n"
            "كم سهماً تريد شراء؟",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ── تأكيد الشراء ──
    elif data.startswith("confirm_buy_"):
        parts = data.split("_")
        sym = parts[2]
        qty = int(parts[3])
        price = get_live_price(sym)
        total_cost = price * qty

        if user["balance"] < total_cost:
            await query.edit_message_text(
                f"❌ رصيدك غير كافٍ!\n"
                f"تحتاج: `{format_money(total_cost)}`\n"
                f"لديك: `{format_money(user['balance'])}`",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="buy_menu")]])
            )
            return

        user["balance"] -= total_cost
        user["portfolio"][sym] = user["portfolio"].get(sym, 0) + qty
        user["transactions"].append({
            "type": "شراء", "symbol": sym, "qty": qty,
            "price": price, "total": total_cost
        })

        await query.edit_message_text(
            f"✅ *تمت عملية الشراء!*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📈 {STOCKS[sym]['name']}: {qty} سهم\n"
            f"💲 بسعر: `{format_money(price)}`\n"
            f"💸 المدفوع: `{format_money(total_cost)}`\n"
            f"💵 الرصيد المتبقي: `{format_money(user['balance'])}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة", callback_data="main_menu")]])
        )

    # ── بيع - قائمة ──
    elif data == "sell_menu":
        if not user["portfolio"]:
            await query.edit_message_text(
                "📁 محفظتك فارغة! اشترِ أسهماً أولاً.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]])
            )
            return
        keyboard = [
            [InlineKeyboardButton(f"{STOCKS[sym]['emoji']} {sym} ({qty} سهم)", callback_data=f"sell_{sym}")]
            for sym, qty in user["portfolio"].items() if qty > 0
        ]
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
        await query.edit_message_text(
            "💸 *اختر السهم للبيع:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ── بيع - اختيار كمية ──
    elif data.startswith("sell_"):
        sym = data.split("_")[1]
        qty_owned = user["portfolio"].get(sym, 0)
        price = get_live_price(sym)
        options = [q for q in [1, 5, 10, qty_owned] if q <= qty_owned]
        keyboard = [
            [InlineKeyboardButton(f"{q} سهم", callback_data=f"confirm_sell_{sym}_{q}")]
            for q in set(options)
        ]
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="sell_menu")])
        await query.edit_message_text(
            f"{STOCKS[sym]['emoji']} *{STOCKS[sym]['name']}*\n"
            f"تملك: {qty_owned} سهم\n"
            f"💲 السعر: `{format_money(price)}`\n\n"
            "كم سهماً تريد بيعه؟",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ── تأكيد البيع ──
    elif data.startswith("confirm_sell_"):
        parts = data.split("_")
        sym = parts[2]
        qty = int(parts[3])
        price = get_live_price(sym)
        total_gain = price * qty

        if user["portfolio"].get(sym, 0) < qty:
            await query.edit_message_text("❌ لا تملك هذا العدد من الأسهم!")
            return

        user["portfolio"][sym] -= qty
        if user["portfolio"][sym] == 0:
            del user["portfolio"][sym]
        user["balance"] += total_gain
        user["transactions"].append({
            "type": "بيع", "symbol": sym, "qty": qty,
            "price": price, "total": total_gain
        })

        await query.edit_message_text(
            f"✅ *تمت عملية البيع!*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📉 {STOCKS[sym]['name']}: {qty} سهم\n"
            f"💲 بسعر: `{format_money(price)}`\n"
            f"💰 المكسب: `{format_money(total_gain)}`\n"
            f"💵 رصيدك الآن: `{format_money(user['balance'])}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة", callback_data="main_menu")]])
        )

    # ── المحفظة ──
    elif data == "portfolio":
        if not user["portfolio"]:
            text = "📁 *محفظتك فارغة*\nاشترِ أسهماً لتبدأ!"
        else:
            text = "📁 *محفظتك الاستثمارية*\n━━━━━━━━━━━━━━━\n"
            total = 0
            for sym, qty in user["portfolio"].items():
                price = get_live_price(sym)
                value = price * qty
                total += value
                text += f"{STOCKS[sym]['emoji']} {sym}: {qty} سهم × `{format_money(price)}` = `{format_money(value)}`\n"
            text += f"━━━━━━━━━━━━━━━\n💼 الإجمالي: `{format_money(total)}`"

        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # ── السجل ──
    elif data == "history":
        txs = user["transactions"][-10:]
        if not txs:
            text = "📜 لا توجد عمليات بعد!"
        else:
            text = "📜 *آخر 10 عمليات:*\n━━━━━━━━━━━━━━━\n"
            for tx in reversed(txs):
                emoji = "🟢" if tx["type"] == "شراء" else "🔴"
                text += f"{emoji} {tx['type']} {tx['qty']} {tx['symbol']} بـ `{format_money(tx['price'])}`\n"

        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # ── المكافأة اليومية ──
    elif data == "bonus":
        bonus = random.uniform(100, 500)
        user["balance"] += bonus
        await query.edit_message_text(
            f"🎁 *مكافأة يومية!*\n"
            f"حصلت على: `{format_money(bonus)}`\n"
            f"💵 رصيدك الآن: `{format_money(user['balance'])}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة", callback_data="main_menu")]])
        )

    # ── القائمة الرئيسية ──
    elif data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("💰 رصيدي", callback_data="balance"),
             InlineKeyboardButton("📊 الأسواق", callback_data="market")],
            [InlineKeyboardButton("🛒 شراء سهم", callback_data="buy_menu"),
             InlineKeyboardButton("💸 بيع سهم", callback_data="sell_menu")],
            [InlineKeyboardButton("📁 محفظتي", callback_data="portfolio"),
             InlineKeyboardButton("📜 سجل العمليات", callback_data="history")],
            [InlineKeyboardButton("🎁 مكافأة يومية", callback_data="bonus")],
        ]
        await query.edit_message_text(
            "📋 *القائمة الرئيسية:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ─────────────────────────────────────────
# تشغيل البوت
# ─────────────────────────────────────────

def main():
    print("🚀 جاري تشغيل البوت...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", show_menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ البوت يعمل الآن!")
    app.run_polling()


if __name__ == "__main__":
    main()
