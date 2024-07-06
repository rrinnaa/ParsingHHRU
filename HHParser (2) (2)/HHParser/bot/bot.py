import sqlite3
import subprocess
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, MessageHandler, Filters


SEARCH, TYPING_KEYWORD, SETTINGS, SETTING_REGION, SETTING_PER_PAGE = range(5)

DATABASE = '/db/vacancies.db'

def get_vacancies_from_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM vacancies')
    rows = c.fetchall()
    conn.close()

    vacancies = []
    for row in rows:
        vacancy = {
            "vacancy_id": row[0],
            "company_id": row[1],
            "company_name": row[2],
            "vacancy_title": row[3],
            "experience": row[4],
            "skills": row[5],
            "salary": row[6],
            "url": row[7],
        }
        vacancies.append(vacancy)
    return vacancies


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Поиск вакансий", callback_data='search'),
            InlineKeyboardButton("Избранные вакансии", callback_data='favorites'),
        ],
        [
            InlineKeyboardButton("Помощь", callback_data='help'),
            InlineKeyboardButton("Настройки", callback_data='settings'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Привет! Выберите действие:', reply_markup=reply_markup)


def start_search(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Введите ключевое слово для поиска:")
    return TYPING_KEYWORD


def received_keyword(update: Update, context: CallbackContext) -> int:
    keyword = update.message.text

    try:
        
        result = subprocess.run(['docker', 'exec', 'vacancy_parser', 'python', 'parser.py', keyword], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(result.stderr)

        vacancies_from_db = get_vacancies_from_db()

        if vacancies_from_db:
            response = "\n\n".join([
                f"ID компании: {vac['company_id']}\n"
                f"Название компании: {vac['company_name']}\n"
                f"Название вакансии: {vac['vacancy_title']}\n"
                f"Опыт работы: {vac['experience']}\n"
                f"Навыки: {vac['skills']}\n"
                f"Зарплата: {vac['salary']}\n"
                f"URL: {vac['url']}\n"
                for vac in vacancies_from_db])
            update.message.reply_text(response)
        else:
            update.message.reply_text('Вакансии не найдены.')
    except Exception as e:
        update.message.reply_text(f"Произошла ошибка при поиске вакансий: {e}")

    return ConversationHandler.END


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'search':
        return start_search(update, context)
    elif query.data == 'favorites':
        query.edit_message_text(text="Избранные вакансии: (в разработке)")
    elif query.data == 'help':
        query.edit_message_text(text="Помощь:\n\nИспользуйте /start для начала.\nВыберите 'Поиск вакансий' для поиска вакансий.\nВыберите 'Избранные вакансии' для просмотра избранных вакансий.\nВыберите 'Настройки' для изменения параметров поиска.")
    elif query.data == 'settings':
        return settings(update, context)


def settings(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.edit_message_text(
        text="Настройки:\n\n1. Изменить регион\n2. Изменить количество вакансий на страницу\n\nВыберите действие:"
    )
    return SETTINGS


def set_region(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Введите ID региона (например, 1 для Москвы):")
    return SETTING_REGION


def set_per_page(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Введите количество вакансий на страницу (например, 10):")
    return SETTING_PER_PAGE


def received_region(update: Update, context: CallbackContext) -> int:
    region = update.message.text
    context.user_data['region'] = region
    update.message.reply_text(f"Регион изменен на {region}.")
    return ConversationHandler.END


def received_per_page(update: Update, context: CallbackContext) -> int:
    per_page = update.message.text
    context.user_data['per_page'] = per_page
    update.message.reply_text(f"Количество вакансий на страницу изменено на {per_page}.")
    return ConversationHandler.END

def main():
    updater = Updater("7147610732:AAFUHQyOWQESURNe0oynQiTw65n3MYTtoHo", use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            TYPING_KEYWORD: [MessageHandler(Filters.text & ~Filters.command, received_keyword)],
            SETTINGS: [
                MessageHandler(Filters.regex('^(1)$'), set_region),
                MessageHandler(Filters.regex('^(2)$'), set_per_page)
            ],
            SETTING_REGION: [MessageHandler(Filters.text & ~Filters.command, received_region)],
            SETTING_PER_PAGE: [MessageHandler(Filters.text & ~Filters.command, received_per_page)],
        },
        fallbacks=[],
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
