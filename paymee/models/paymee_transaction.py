from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
import logging

_logger = logging.getLogger(__name__)


#
# This is a model class named PaymeeTransaction in Odoo that inherits from payment.transaction model.
# It adds custom fields and methods to handle Paymee payment gateway related data and actions.
#
# Here's what each method in the class does:
#
# It checks the currency and amount values in the data against the transaction record in Odoo and returns a list of any invalid parameters.
# It checks the status key in the data to determine if the payment was successful or not, updates the payment transaction record in Odoo with :
# the Paymee transaction token, acquirer reference, and state, and returns True if the payment was successful, or False if it failed.

#

class PaymeeTransaction(models.Model):
    _inherit = 'payment.transaction'
    # The paymee_txn_token field is a custom field that stores the Paymee transaction token
    # associated with the payment transaction in Odoo.

    paymee_txn_token = fields.Char('Paymee Transaction Token')

    # _paymee_form_get_tx_from_data:
    # This method is called when
    # Paymee payment gateway sends transaction data back to Odoo after payment.
    @api.model
    def _paymee_form_get_tx_from_data(self, data):
        reference = data.get('reference')
        if not reference:
            error_msg = _('Paymee: received data with missing reference (%s)') % reference
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # It uses the reference key in the data to search for the corresponding payment transaction record in Odoo and returns it.
        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = _('Paymee: received data for reference %s') % reference
            if not tx:
                error_msg += _('; no transaction found')
            else:
                error_msg += _('; multiple transactions found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx

    # _paymee_form_get_invalid_parameters:
    # This method is called to validate the transaction data received from Paymee.
    def _paymee_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        if self.currency_id.name != data.get('currency'):
            invalid_parameters.append(('Currency', data.get('currency'), self.currency_id.name))

        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('Amount', data.get('amount'), '%.2f' % self.amount))

        return invalid_parameters

    # _paymee_form_validate:
    # This method is called to validate and process the transaction data received from Paymee.
    def _paymee_form_validate(self, data):
        status = data.get('status')
        tx_state = 'done' if status == 'PAID' else 'error'
        tx = self.env['payment.transaction'].search([('reference', '=', data.get('reference'))])
        tx.write({
            'paymee_txn_token': data.get('token'),
            'state': tx_state,
            'acquirer_reference': data.get('id'),
            'date': fields.datetime.now(),
        })
        if status != 'PAID':
            error = 'Paymee: feedback error'
            if data.get('response_code'):
                error += ' (%s: %s)' % (data['response_code'], data['response_message'])
            tx.write({'state_message': error})
            tx._set_transaction_cancel()
            return False
        return True
