from odoo import models, fields, api
from odoo.tools import float_compare


class PaymeePaymentWizard(models.TransientModel):
    _name = 'paymee.payment.wizard'

    # fields for payment information
    amount = fields.Float(string='Amount')
    note = fields.Char(string='Note')
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    return_url = fields.Char(string='Return URL')
    cancel_url = fields.Char(string='Cancel URL')
    webhook_url = fields.Char(string='Webhook URL')
    order_id = fields.Char(string='Order ID')

    @api.model
    def create(self, vals):
        # retrieve the sale order from the context
        order_id = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].browse(order_id)

        # set payment information fields based on sale order information
        vals.update({
            'amount': sale_order.amount_total,
            'note': f'Order #{sale_order.name}',
            'first_name': sale_order.partner_id.firstname,
            'last_name': sale_order.partner_id.lastname,
            'email': sale_order.partner_id.email,
            'phone': sale_order.partner_id.phone,
            'order_id': sale_order.name,
            'return_url': 'https://www.return_url.tn',
            'cancel_url': 'https://www.cancel_url.tn',
            'webhook_url': 'https://www.webhook_url.tn',
        })

        return super(PaymeePaymentWizard, self).create(vals)
