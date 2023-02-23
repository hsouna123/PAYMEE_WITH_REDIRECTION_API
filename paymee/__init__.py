from odoo import api, SUPERUSER_ID
from . import models
from . import controllers


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    controllers._register_http_controllers()
