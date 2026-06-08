# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from . import models
from . import wizard
from . import controllers


# This is the hook that Odoo will call (must accept 'cr, registry')
def post_init_hook(cr, registry):
    from .hooks import post_init_hook as _demo_hook
    _demo_hook(cr, registry)