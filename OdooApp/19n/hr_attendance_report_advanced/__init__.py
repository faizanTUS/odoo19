# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from . import models
from . import controllers
from . import wizard
from . import reports

# Import post_init_hook for manifest
from .models.post_init_hook import post_init_hook