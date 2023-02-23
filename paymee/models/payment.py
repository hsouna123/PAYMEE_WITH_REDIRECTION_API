from odoo import api, fields, models, _
import requests


class PaymeePayment(models.TransientModel):
    _name = 'paymee.payment'

    amount = fields.Float(string='Amount', required=True)
    note = fields.Char(string='Note', required=True)
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    return_url = fields.Char(string='Return URL', required=True)
    cancel_url = fields.Char(string='Cancel URL', required=True)
    webhook_url = fields.Char(string='Webhook URL', required=True)
    order_id = fields.Char(string='Order ID')

    def paymee_payment_redirect(self):
        api_key = 'c79d9ec616b0d8f5e306bc64fc29af32c7f19320'
        sandbox_url = 'https://sandbox.paymee.tn/api/v2/payments/create'
        headers = {'Content-Type': 'application/json', 'Authorization': 'Token %s' % api_key}

        input_data = {
            "amount": self.amount,
            "note": self.note,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "return_url": self.return_url,
            "cancel_url": self.cancel_url,
            "webhook_url": self.webhook_url,
            "order_id": self.order_id,
        }

        response = requests.post(sandbox_url, headers=headers, json=input_data)

        if response.status_code == 200:
            result = response.json().get('data')
            return {
                'type': 'ir.actions.act_url',
                'url': result.get('payment_url'),
                'target': 'new',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'paymee.payment',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {
                    'default_amount': self.amount,
                    'default_note': self.note,
                    'default_first_name': self.first_name,
                    'default_last_name': self.last_name,
                    'default_email': self.email,
                    'default_phone': self.phone,
                    'default_return_url': self.return_url,
                    'default_cancel_url': self.cancel_url,
                    'default_webhook_url': self.webhook_url,
                    'default_order_id': self.order_id,
                },
            }
