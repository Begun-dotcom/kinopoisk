from app.config import setting


def start_kb(data: list, user_id: int = None):
    list_kb = []
    if user_id:
        for value in data:
            # Пропускаем админскую кнопку если пользователь не админ
            if value == "⚙️ Адм.панель" and user_id not in setting.ADMIN_IDS:
                continue
            list_kb.append(value)
    else:
        for value in data:
            list_kb.append(value)
    return list_kb