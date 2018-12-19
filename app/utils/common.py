import functools

from flask import session, current_app, g


def do_index_class(index):
    """自定义过滤器，过滤点击排序html的class"""
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    else:
        return ""


def user_login_data(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        user = None
        if user_id:
            from app.models import User
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        # 不能写在if的里面，否则如果没有用户登录，就不会有g.user这个东西，就会报错（哪怕有个None也不会报错）
        g.user = user
        return view_func(*args, **kwargs)

    return wrapper
