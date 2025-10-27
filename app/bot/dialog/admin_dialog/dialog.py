from aiogram_dialog import Dialog

from app.bot.dialog.admin_dialog.windows import get_log_window, add_banner_windows

admin_panel = Dialog(
    get_log_window(),

)
admin_banner = Dialog(
    add_banner_windows()
)