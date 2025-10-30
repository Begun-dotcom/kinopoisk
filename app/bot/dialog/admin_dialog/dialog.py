from aiogram_dialog import Dialog

from app.bot.dialog.admin_dialog.windows import get_log_window, add_banner_windows, input_name_table_window, \
    get_status_window

admin_panel = Dialog(
    get_log_window(),

)
admin_banner = Dialog(
input_name_table_window(),
    add_banner_windows()
)

admin_user_count = Dialog(
get_status_window()
)