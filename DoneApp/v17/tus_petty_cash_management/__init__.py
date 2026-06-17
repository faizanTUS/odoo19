# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from . import models
from . import wizard
from . import controllers


def post_init_hook(env):
    from .hooks import post_init_hook as _hook

    _hook(env.cr, env.registry)
