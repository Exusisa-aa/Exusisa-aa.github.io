# -*- coding: utf-8 -*-
"""限流器 —— 单独放一个模块，避免 main.py 与 api/*.py 互相 import 成环。"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
