from functools import wraps
from database.models import User

def with_user(handler):
    @wraps(handler)
    async def wrapper(update, context, *args, **kwargs):
        tg_user = update.effective_user
        user, _ = User.get_or_create(
            telegram_id=tg_user.id,
            defaults={
                "username": tg_user.username,
                "first_name": tg_user.first_name
            }
        )
        context.user_db = user
        return await handler(update, context, *args, **kwargs)
    return wrapper
