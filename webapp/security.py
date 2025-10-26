import hmac, hashlib, os, urllib.parse
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # тот же, что TOKEN у бота

def check_init_data(init_data: str) -> dict | None:
    """
    Возвращает dict данных пользователя из initData, если подпись валидна.
    Спецификация: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    if not BOT_TOKEN or not init_data:
        return None
    # init_data — строка querystring. Нужно выделить hash=… и рассчитать HMAC на основе остального.
    data = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
    hash_recv = data.pop('hash', None)
    if not hash_recv:
        return None
    # Сортируем ключи, собираем строку
    check_str = "\n".join(f"{k}={data[k]}" for k in sorted(data.keys()))
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    h = hmac.new(secret_key, msg=check_str.encode(), digestmod=hashlib.sha256).hexdigest()
    if h != hash_recv:
        return None
    return data  # содержит user=JSON,…, auth_date, query_id и т.д.
