from odoo import api, fields, models
import requests
from odoo import http
from odoo.http import request


class PaymeePayment(models.Model):
    _name = 'paymee.payment'
    _description = 'Paymee Payment'

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

    def initiate_payment(self):
        # Make a POST request to Paymee's sandbox URL
        url = 'https://sandbox.paymee.tn/api/v2/payments/create'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Token c79d9ec616b0d8f5e306bc64fc29af32c7f19320'
        }
        payload = {
            'amount': self.amount,
            'note': self.note,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'return_url': self.return_url,
            'cancel_url': self.cancel_url,
            'webhook_url': self.webhook_url,
            'order_id': self.order_id
        }
        response = requests.post(url, headers=headers, json=payload)

        # Parse the response from Paymee and extract the payment_url field
        data = response.json().get('data')
        payment_url = data.get('payment_url')

        # Redirect the user to the payment_url
        return {
            'type': 'ir.actions.act_url',
            'url': payment_url,
            'target': 'new',
        }

    @api.model
    def _get_paymee_button(self, **kwargs):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/paymee-initiate/%d' % self.id,
            'target': 'new',
        }

    @http.route('/paymee-initiate/<int:order_id>', type='http', auth='public', website=True)
    def initiate_payment_route(self, order_id=None, **kwargs):
        order = request.env['sale.order'].sudo().browse(order_id)
        # Make a POST request to Paymee's sandbox URL
        url = 'https://sandbox.paymee.tn/api/v2/payments/create'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Token c79d9ec616b0d8f5e306bc64fc29af32c7f19320'
        }
        payload = {
            'amount': order.amount_total,
            'note': 'Order #{}'.format(order.name),
            'first_name': order.partner_id.name,
            'last_name': '',
            'email': order.partner_id.email,
            'phone': order.partner_id.phone,
            'return_url': 'https://www.return_url.tn',
            'cancel_url': 'https://www.cancel_url.tn',
            'webhook_url': 'https://www.webhook_url.tn',
            'order_id': str(order.id)
        }
        response = requests.post(url, headers=headers, json=payload)
        # Parse the response from Paymee and extract the payment_url field
        data = response.json().get('data')
        payment_url = data.get('payment_url')
        # Redirect the user to the payment_url
        return http.redirect_with_hash(payment_url)

    @http.route('/payment/paymee/dpn', type='http', auth='none', methods=['POST'], csrf=False)
    def dpn(self, **post):
        # Retrieve the request payload
        payload = post.get('payload')
        # Do something with the payload, such as updating the order's payment status
        order_id = payload.get('order_id')
        status = payload.get('status')
        # ...

        # Return a response to acknowledge receipt of the payload
        return 'OK'
