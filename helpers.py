from functools import wraps
from flask import redirect, render_template, request, session
from datetime import datetime
from time import time, mktime, strptime

# Login required wrapper function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function
