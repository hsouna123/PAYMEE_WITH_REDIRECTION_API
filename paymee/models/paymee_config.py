from odoo import models, fields


class PaymeeConfig(models.Model):
    _name = 'paymee.config'
    _description = 'Paymee Configuration'

    provider = fields.Char(string='Provider')
    api_key = fields.Char(string='API Key')
    secret_key = fields.Char(string='Secret Key')
    token = fields.Char(string='Token')
