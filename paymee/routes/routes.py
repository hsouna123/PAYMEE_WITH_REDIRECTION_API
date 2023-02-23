from odoo import http
from .controllers import PaymeeControllers


def paymee_routes():
    http.route('/paymee-initiate', type='http', auth='public', website=True, csrf=False)(
        PaymeeControllers.initiate_payment)
    http.route('/paymee-return', type='http', auth='public', website=True, csrf=False)(
        PaymeeControllers.return_payment)
    http.route('/paymee-cancel', type='http', auth='public', website=True, csrf=False)(
        PaymeeControllers.cancel_payment)
    http.route('/paymee-webhook', type='http', auth='public', website=True, csrf=False)(
        PaymeeControllers.webhook_payment)
