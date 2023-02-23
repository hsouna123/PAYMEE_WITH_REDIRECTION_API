import requests
import json
from odoo import api, fields, models, _


# When a user selects Paymee as the payment method for a product,
# the paymee_form_generate_values method is called to generate the necessary data to send to Paymee,
# and then a request is made to the Paymee API to create the payment transaction.
# Once the transaction is created, the user is redirected to the Paymee payment page to complete the transaction.

# After the user completes the transaction, the Paymee API sends a response to a webhook URL provided in the request.
# The PaymeeTransaction._paymee_form_validate method handles this response by updating :
# the payment,  transaction record in Odoo with the transaction status, transaction token, and other details.
#
class PaymeeAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('paymee', 'Paymee')], tracking=True, ondelete={'paymee': 'set default'})
    paymee_api_key = fields.Char('Paymee API Key')
    paymee_base_url = fields.Char('Paymee Base URL')

    @api.model
    def _get_providers(self):
        providers = super(PaymeeAcquirer, self)._get_providers()
        providers.append(('paymee', _('Paymee')))
        return providers

    def paymee_form_generate_values(self, values):
        base_url = self.paymee_base_url
        amount = super(values.get('amount', self.amount))
        paymee_currency = values.get('currency', self.currency_id.name)
        paymee_reference = values.get('reference', '')
        paymee_api_key = self.paymee_api_key
        paymee_order_id = self.reference_prefix + "-" + str(self.id)
        paymee_success_url = self.return_url
        paymee_failure_url = self.cancel_url
        paymee_cancel_url = self.cancel_url

        data = {
            'amount': amount,
            'note': paymee_reference,
            'first_name': values.get('partner_first_name', ''),
            'last_name': values.get('partner_last_name', ''),
            'email': values.get('partner_email', ''),
            'phone': values.get('partner_phone', ''),
            'return_url': paymee_success_url,
            'cancel_url': paymee_cancel_url,
            'webhook_url': '/payment/paymee/s2s',
            'order_id': paymee_order_id,
        }

        headers = {
            'Authorization': f'Token {paymee_api_key}',
            'Content-Type': 'application/json',
        }

        r = requests.post(f'{base_url}/payments/create', data=json.dumps(data), headers=headers)
        response = r.json()
        paymee_token = response.get('data', {}).get('token', '')

        paymee_form_data = {
            'paymee_token': paymee_token,
            'paymee_base_url': base_url,
            'paymee_success_url': paymee_success_url,
        }

        return paymee_form_data
