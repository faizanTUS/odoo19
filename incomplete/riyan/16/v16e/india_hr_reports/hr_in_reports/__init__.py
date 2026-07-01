# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo.api import Environment
from odoo import _

if not hasattr(Environment, '_'):
    def env_translate(self, source, *args, **kwargs):
        return _(source, *args, **kwargs)
    Environment._ = env_translate

from . import models
from . import reports
