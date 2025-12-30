# Импорт необходимых модулей.
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
import yt_dlp  # Для работы с VK видео
import os
import logging  # Для логирования ошибок
import asyncio
import re
import hashlib
import time

# Настройка логирования для дебаггинга.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определение состояний разговора.
LINK = 0
CHOOSE_QUALITY = 1

# Максимальный размер файла для Telegram (в байтах)
MAX_FILE_SIZE = 150 * 1024 * 1024  # 15MB - лимит Telegram

# Максимальная длительность видео (в секундах)
MAX_DURATION = 6000  # 100 минут

# Глобальные переменные для отслеживания
active_downloads = {}
user_video_data = {}


def normalize_url(link):
    """Преобразование vkvideo.ru в vk.com и очистка URL"""
    if not link:
        return ""
    link = str(link).strip()
    if 'vkvideo.ru' in link:
        link = link.replace('vkvideo.ru', 'vk.com')
    if not link.startswith(('http://', 'https://')):
        link = 'https://' + link
    return link


def is_valid_vk_url(url):
    """Проверяет, является ли ссылка валидной VK ссылкой"""
    if not url:
        return False
    patterns = [
        r'https?://vk\.com/.*video.*',
        r'https?://vk\.com/.*clip.*',
        r'https?://vk\.com/video.*',
        r'https?://vkvideo\.ru/.*'
    ]
    for pattern in patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return True
    return False


def get_video_info_with_formats(url):
    """Получает информацию о видео и доступные форматы"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'socket_timeout': 30,
        'retries': 3,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        # Собираем доступные форматы
        formats = []
        if 'formats' in info:
            for fmt in info['formats']:
                if fmt.get('vcodec') != 'none':  # Только видео форматы
                    # Получаем качество, если доступно, иначе используем 0
                    quality = fmt.get('quality', 0)
                    if quality is None:
                        quality = 0

                    formats.append({
                        'format_id': fmt.get('format_id', ''),
                        'height': fmt.get('height', 0),
                        'width': fmt.get('width', 0),
                        'filesize': fmt.get('filesize'),
                        'ext': fmt.get('ext', ''),
                        'format_note': fmt.get('format_note', ''),
                        'quality': quality,
                    })

        return {
            'title': info.get('title', 'Без названия') or 'Без названия',
            'duration': info.get('duration', 0) or 0,
            'formats': formats,
            'best_format': info.get('format_id', 'best') or 'best',
            'thumbnail': info.get('thumbnail', '') or '',
            'uploader': info.get('uploader', 'Неизвестно') or 'Неизвестно',
            'view_count': info.get('view_count', 0) or 0,
            'original_url': url
        }


def format_duration(seconds):
    """Форматирует длительность в читаемый вид"""
    if not seconds or seconds == 0:
        return "Неизвестно"
    try:
        seconds = int(seconds)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes} мин {seconds} сек"
    except:
        return "Неизвестно"


def format_size(size_bytes):
    """Форматирует размер в читаемый вид"""
    if not size_bytes:
        return "Неизвестно"

    try:
        size_bytes = float(size_bytes)
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} B"
        elif size_bytes < 1024.0 * 1024.0:
            return f"{size_bytes / 1024.0:.1f} KB"
        elif size_bytes < 1024.0 * 1024.0 * 1024.0:
            return f"{size_bytes / (1024.0 * 1024.0):.1f} MB"
        else:
            return f"{size_bytes / (1024.0 * 1024.0 * 1024.0):.1f} GB"
    except:
        return "Неизвестно"


def filter_formats_by_size(formats):
    """Фильтрует форматы по размеру, оставляя только те, что меньше MAX_FILE_SIZE"""
    filtered_formats = []
    for fmt in formats:
        filesize = fmt.get('filesize')
        if filesize and filesize <= MAX_FILE_SIZE:
            filtered_formats.append(fmt)
        elif not filesize:  # Если размер неизвестен, оставляем
            filtered_formats.append(fmt)
    return filtered_formats


async def start(update: Update, context):
    """Обработчик команды /start"""
    await update.message.reply_text(
        '👋 Привет! Я бот для скачивания видео из VK.\n\n'
        '📹 Возможности:\n'
        '• Скачивание видео до 100 минут\n'
        '• Выбор качества загрузки\n'
        '• Поддержка ссылок vk.com и vkvideo.ru\n\n'
        '⚠️ Ограничения:\n'
        '• Максимальный размер: 150MB (ограничение Telegram)\n'
        '• Видео должно быть публичным\n'
        '• Только видео, которые помещаются в лимит\n\n'
        '📝 Как использовать:\n'
        '1. Отправьте ссылку на видео VK\n'
        '2. Бот проанализирует доступные форматы\n'
        '3. Выберите качество, которое помещается в 150MB\n'
        '4. Получите видео\n\n'
        'Отправьте ссылку или /cancel для отмены.'
    )
    return LINK


async def get_link(update: Update, context):
    """Обработчик получения ссылки"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Проверяем, есть ли текст сообщения
    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Пожалуйста, отправьте ссылку на видео.")
        return LINK

    original_link = update.message.text.strip()

    # Проверяем активные загрузки
    if user_id in active_downloads:
        await update.message.reply_text(
            "⏳ У вас уже есть активная загрузка. Пожалуйста, дождитесь ее завершения."
        )
        return LINK

    # Нормализуем URL
    link = normalize_url(original_link)

    # Проверяем валидность ссылки
    if not is_valid_vk_url(link):
        await update.message.reply_text(
            "❌ Это не похоже на ссылку VK видео. Пожалуйста, отправьте корректную ссылку.\n"
            "Примеры:\n"
            "• https://vk.com/video-123456789_456239017\n"
            "• https://vk.com/clip-123456789_456239017\n"
            "• https://vkvideo.ru/video-123456789_456239017"
        )
        return LINK

    # Добавляем пользователя в активные загрузки
    active_downloads[user_id] = True

    try:
        # Получаем информацию о видео
        status_msg = await update.message.reply_text("📥 Получаю информацию о видео...")

        video_info = get_video_info_with_formats(link)

        # Проверяем длительность
        duration = video_info['duration']
        if duration > MAX_DURATION:
            await status_msg.edit_text(
                f"❌ Видео слишком длинное ({format_duration(duration)}).\n"
                f"Максимальная длительность: {format_duration(MAX_DURATION)}.\n"
                "Попробуйте найти более короткое видео."
            )
            del active_downloads[user_id]
            return LINK

        # Сохраняем информацию о видео
        user_video_data[user_id] = {
            'link': link,
            'info': video_info,
            'status_message': status_msg
        }

        # Фильтруем форматы по размеру
        available_formats = filter_formats_by_size(video_info['formats'])

        if not available_formats:
            # Нет подходящих форматов
            await status_msg.edit_text(
                f"❌ Все доступные форматы этого видео превышают лимит Telegram ({MAX_FILE_SIZE / (1024 * 1024):.0f}MB).\n\n"
                "Попробуйте найти видео меньшего размера или другую ссылку."
            )
            del active_downloads[user_id]
            return LINK

        # Формируем информацию о видео для пользователя
        title = video_info['title']
        if len(title) > 100:
            title = title[:100] + "..."

        # Форматируем количество просмотров
        view_count = video_info['view_count']
        view_count_str = "Неизвестно"
        if view_count and view_count > 0:
            try:
                view_count_str = f"{view_count:,}"
            except:
                view_count_str = str(view_count)

        info_text = (
            f"🎬 {title}\n\n"
            f"📊 Информация:\n"
            f"• Длительность: {format_duration(duration)}\n"
            f"• Автор: {video_info['uploader']}\n"
            f"• Просмотров: {view_count_str}\n"
        )

        # Проверяем, есть ли формат с известным размером
        has_known_size = any(fmt.get('filesize') for fmt in available_formats)

        if has_known_size:
            info_text += f"✅ Найдены форматы, которые помещаются в лимит Telegram.\n\n"
        else:
            info_text += f"⚠️ Размер видео неизвестен. Бот попробует скачать в выбранном качестве.\n\n"

        await status_msg.edit_text(info_text, parse_mode=ParseMode.MARKDOWN)

        # Группируем форматы по высоте для отображения
        unique_formats = {}
        for fmt in available_formats:
            height = fmt.get('height', 0)
            if height is None:
                height = 0

            # Получаем качество с безопасной обработкой None
            current_quality = fmt.get('quality', 0)
            if current_quality is None:
                current_quality = 0

            # Получаем качество существующего формата
            existing_quality = unique_formats.get(height, {}).get('quality', 0)
            if existing_quality is None:
                existing_quality = 0

            # Если нет формата с такой высотой или текущее качество лучше
            if height not in unique_formats or current_quality > existing_quality:
                unique_formats[height] = fmt

        # Сортируем по высоте
        sorted_heights = sorted([h for h in unique_formats.keys() if h is not None], reverse=True)

        if not sorted_heights:
            # Если нет форматов с указанной высотой
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Не удалось определить доступные качества видео."
            )
            del active_downloads[user_id]
            return LINK

        if len(sorted_heights) == 1:
            # Если только один формат, скачиваем сразу
            height = sorted_heights[0]
            fmt = unique_formats[height]
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🔄 Начинаю скачивание в качестве {height}p..."
            )
            await download_video(update, context, user_id, link, fmt['format_id'])
            return ConversationHandler.END
        else:
            # Предлагаем выбор качества
            keyboard = []
            row = []
            for i, height in enumerate(sorted_heights):
                if i >= 8:  # Ограничиваем количество вариантов
                    break

                fmt = unique_formats[height]
                size_text = format_size(fmt.get('filesize')) if fmt.get('filesize') else "?"
                button_text = f"{height}p ({size_text})"
                row.append(InlineKeyboardButton(button_text, callback_data=f'quality_{fmt["format_id"]}'))

                # Добавляем по 2 кнопки в ряд
                if len(row) == 2 or i == len(sorted_heights) - 1:
                    keyboard.append(row)
                    row = []

            # Добавляем кнопку "Отмена"
            keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data='cancel_download')])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=chat_id,
                text="🎚️ Выберите качество видео:\n\n"
                     "Чем выше качество, тем больше размер файла.\n"
                     "Все представленные форматы должны помещаться в лимит 150MB.",
                reply_markup=reply_markup
            )
            return CHOOSE_QUALITY

    except Exception as e:
        logger.error(f"Ошибка при получении информации: {e}", exc_info=True)
        error_message = f"❌ Ошибка: {str(e)}"
        if "Private video" in str(e) or "Доступ запрещен" in str(e):
            error_message = "❌ Это приватное видео или видео недоступно.\nЯ могу скачивать только публичные видео."
        elif "Video unavailable" in str(e) or "Не найдено" in str(e):
            error_message = "❌ Видео не найдено или было удалено.\nПроверьте правильность ссылки."
        elif "Unsupported URL" in str(e):
            error_message = "❌ Неподдерживаемая ссылка.\nУбедитесь, что это ссылка на видео VK."

        await update.message.reply_text(error_message)
        if user_id in active_downloads:
            del active_downloads[user_id]
        if user_id in user_video_data:
            del user_video_data[user_id]
        return LINK


async def handle_quality_choice(update: Update, context):
    """Обработчик выбора качества"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data == 'cancel_download':
        await query.edit_message_text("❌ Загрузка отменена.")
        if user_id in active_downloads:
            del active_downloads[user_id]
        if user_id in user_video_data:
            del user_video_data[user_id]
        return ConversationHandler.END
    else:
        # Пользователь выбрал конкретное качество
        format_id = query.data.replace('quality_', '')

        await query.edit_message_text(f"🔄 Начинаю скачивание...")

        user_data = user_video_data.get(user_id, {})
        if user_data:
            await download_video(update, context, user_id, user_data['link'], format_id)
        else:
            await query.edit_message_text("❌ Данные устарели. Начните заново.")

        return ConversationHandler.END


async def download_video(update: Update, context, user_id: int, link: str, quality: str):
    """Скачивает и отправляет видео"""
    try:
        chat_id = update.effective_chat.id

        # Создаем уникальное имя файла
        unique_id = hashlib.md5(f"{link}_{quality}".encode()).hexdigest()[:8]
        output_template = f'downloads/{unique_id}_%(title)s.%(ext)s'

        # Настраиваем yt-dlp
        ydl_opts = {
            'format': quality if quality != 'best' else 'best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 60,
            'retries': 10,
            'fragment_retries': 10,
            'extractor_retries': 3,
            'http_chunk_size': 1048576,
            'noplaylist': True,
        }

        await context.bot.send_message(
            chat_id=chat_id,
            text="⬇️ Скачиваю видео... Это может занять некоторое время."
        )

        # Скачиваем видео
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(link, download=True)

            # Получаем путь к скачанному файлу
            if 'requested_downloads' in result and result['requested_downloads']:
                filepath = result['requested_downloads'][0]['filepath']
            else:
                filepath = ydl.prepare_filename(result)

            # Проверяем существование файла
            if not os.path.exists(filepath):
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Не удалось скачать видео. Попробуйте другую ссылку."
                )
                return

            # Проверяем размер файла
            file_size = os.path.getsize(filepath)

            if file_size > MAX_FILE_SIZE:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ Видео оказалось слишком большим ({format_size(file_size)}).\n"
                         f"Максимальный размер для Telegram: {format_size(MAX_FILE_SIZE)}.\n\n"
                         "Попробуйте выбрать более низкое качество или другую ссылку."
                )

                # Удаляем временный файл
                if os.path.exists(filepath):
                    os.remove(filepath)
            else:
                # Пытаемся отправить видео с повторными попытками
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        if attempt > 0:
                            await context.bot.send_message(
                                chat_id=chat_id,
                                text=f"🔄 Попытка {attempt + 1} из {max_retries}..."
                            )

                        # Отправляем видео с увеличенными таймаутами
                        with open(filepath, 'rb') as video_file:
                            await context.bot.send_video(
                                chat_id=chat_id,
                                video=video_file,
                                caption="✅ Видео успешно скачано!",
                                read_timeout=300,  # Увеличено до 300 секунд
                                write_timeout=300,  # Увеличено до 300 секунд
                                connect_timeout=300,  # Увеличено до 300 секунд
                                pool_timeout=300  # Увеличено до 300 секунд
                            )

                        break  # Успешно отправлено, выходим из цикла

                    except Exception as e:
                        logger.error(f"Ошибка при отправке видео (попытка {attempt + 1}): {e}")

                        if attempt == max_retries - 1:
                            # Последняя попытка не удалась
                            await context.bot.send_message(
                                chat_id=chat_id,
                                text=f"❌ Не удалось отправить видео после {max_retries} попыток.\n"
                                     "Попробуйте выбрать более низкое качество или другую ссылку."
                            )
                        else:
                            # Ждем перед следующей попыткой
                            await asyncio.sleep(5)

                # Удаляем временный файл
                if os.path.exists(filepath):
                    os.remove(filepath)

                await context.bot.send_message(
                    chat_id=chat_id,
                    text="✅ Готово! Можете отправить следующую ссылку."
                )

    except Exception as e:
        logger.error(f"Ошибка скачивания: {e}", exc_info=True)
        error_message = f"❌ Ошибка при скачивании: {str(e)[:200]}"

        if "File larger than max-filesize" in str(e):
            error_message = "❌ Видео слишком большое для скачивания.\nПопробуйте выбрать более низкое качество."
        elif "403" in str(e) or "Forbidden" in str(e):
            error_message = "❌ Доступ к видео запрещен.\nВозможно, видео приватное или требуется авторизация."
        elif "404" in str(e) or "Not Found" in str(e):
            error_message = "❌ Видео не найдено.\nПроверьте правильность ссылки."
        elif "ReadError" in str(e) or "таймаут" in str(e).lower():
            error_message = "❌ Таймаут при отправке видео.\nПопробуйте выбрать более низкое качество или другую ссылку."

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_message
        )
    finally:
        # Очищаем данные пользователя
        if user_id in active_downloads:
            del active_downloads[user_id]
        if user_id in user_video_data:
            del user_video_data[user_id]


async def cancel(update: Update, context):
    """Обработчик команды /cancel"""
    user_id = update.effective_user.id

    if user_id in active_downloads:
        del active_downloads[user_id]
    if user_id in user_video_data:
        del user_video_data[user_id]

    await update.message.reply_text(
        "❌ Операция отменена.\n\n"
        "Для начала работы отправьте /start или ссылку на видео."
    )
    return ConversationHandler.END


async def help_command(update: Update, context):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "📖 Помощь по использованию бота:\n\n"
        "📹 Как скачать видео:\n"
        "1. Отправьте ссылку на видео из VK\n"
        "2. Бот проанализирует доступные форматы\n"
        "3. Выберите качество, которое помещается в 50MB\n"
        "4. Получите видео\n\n"
        "⚡ Особенности:\n"
        "• Максимальный размер видео: 150MB (ограничение Telegram)\n"
        "• Максимальная длительность: 100 минут\n"
        "• Только публичные видео\n"
        "• Поддерживаются ссылки vk.com и vkvideo.ru\n\n"
        "📝 Примеры ссылок:\n"
        "• https://vk.com/video-123456789_456239017\n"
        "• https://vk.com/clip-123456789_456239017\n"
        "• https://vkvideo.ru/video-123456789_456239017\n\n"
        "🎚️ О качестве видео:\n"
        "• Бот автоматически фильтрует форматы по размеру\n"
        "• Выбирайте самое высокое качество из доступных\n"
        "• Если видео большое, выбирайте более низкое качество\n\n"
        "🔄 Команды:\n"
        "/start - начать работу\n"
        "/help - показать помощь\n"
        "/cancel - отменить текущую операцию\n\n"
        "⚠️*Если возникли проблемы:\n"
        "1. Убедитесь, что видео публичное\n"
        "2. Проверьте правильность ссылки\n"
        "3. Попробуйте другую ссылку\n"
        "Для начала просто отправьте ссылку на видео!"
    )


async def error_handler(update: Update, context):
    """Глобальный обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}", exc_info=True)

    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Произошла ошибка. Попробуйте еще раз или используйте /start для перезапуска."
            )
        except:
            pass

    # Очищаем данные пользователя при ошибке
    if update and update.effective_user:
        user_id = update.effective_user.id
        if user_id in active_downloads:
            del active_downloads[user_id]
        if user_id in user_video_data:
            del user_video_data[user_id]


def main():

    TOKEN = '7898058610:AAE92t_hegNZG6R-31y2o5kMZ48skY9P3Ow'

    # Создаем Application с увеличенными таймаутами
    application = Application.builder() \
        .token(TOKEN) \
        .read_timeout(300) \
        .write_timeout(300) \
        .connect_timeout(300) \
        .pool_timeout(300) \
        .build()

    # Добавляем глобальный обработчик ошибок
    application.add_error_handler(error_handler)

    # Создаем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)
        ],
        states={
            LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)
            ],
            CHOOSE_QUALITY: [
                CallbackQueryHandler(handle_quality_choice, pattern='^(quality_.*|cancel_download)$')
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', start),
            CommandHandler('help', help_command)
        ],
        allow_reentry=True,
        conversation_timeout=300  # 5 минут
    )

    # Добавляем обработчики команд
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('cancel', cancel))

    # Создаем папку для загрузок
    os.makedirs('downloads', exist_ok=True)

    # Запускаем бота
    logger.info("Бот запущен")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}", exc_info=True)