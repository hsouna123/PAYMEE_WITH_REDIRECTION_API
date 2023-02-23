from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PaymeeController(http.Controller):

    @http.route(['/payment/paymee/s2s'], type='json', auth='none', csrf=False)
    def paymee_s2s_notification(self, **post):
        _logger.info('Beginning Paymee s2s notification handling')

        if post:
            _logger.info('Received notification data: %s' % post)

            # Retrieve the payment object
            reference = post.get('order_id', False)
            if reference:
                payment = request.env['payment.transaction'].search([('reference', '=', reference)])
                if payment:
                    status = post.get('status', False)
                    if status == 'approved':
                        payment.write({
                            'acquirer_reference': post.get('token'),
                            'date_validate': fields.datetime.now(),
                        })
                        payment._set_transaction_done()
                        return 'OK'
                    elif status == 'cancelled':
                        payment._set_transaction_cancel()
                        return 'OK'
                    else:
                        error = 'Paymee: feedback error'
                        _logger.warning(error)
                        return error
                else:
                    error = 'Paymee: payment not found'
                    _logger.warning(error)
                    return error
            else:
                error = 'Paymee: received data with missing reference'
                _logger.warning(error)
                return error
        else:
            error = 'Paymee: received empty notification'
            _logger.warning(error)
            return error
