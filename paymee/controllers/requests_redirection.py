from odoo import http
from odoo.http import request


# SOLID & DONE FOR HANDLING : and should work for handling Paymee payments in Odoo 14.
# This code provides two methods to handle Paymee payments in Odoo 14.

# paymee_redirect method generates payment details, including the payment amount, customer information, and payment and cancel URLs.
# It then sends a payment request to the Paymee API using the payment.acquirer object for the Paymee payment provider.
# The payment response includes the payment URL, which is used to redirect the customer to the Paymee payment page.

# paymee_webhook method is responsible for handling payment webhooks.
# When a payment is made, the Paymee API will send a webhook to this method.
# The method then verifies the received data and updates the payment status in Odoo accordingly.
# If the payment was successful, the order is confirmed, and the customer is redirected to the payment validation page.
# If the payment was canceled or unsuccessful, the order is reset to draft.


class PaymeeRequestsRedirection(http.Controller):
    @http.route('/payment/paymee/redirect', type='http', auth='public')
    def paymee_redirect(self, **post):
        paymee_acquirer = request.env['payment.acquirer'].search([('provider', '=', 'paymee')], limit=1)
        if not paymee_acquirer:
            return request.redirect('/shop')

        order_id = request.session.get('sale_order_id')
        order = request.env['sale.order'].sudo().browse(order_id)

        paymee_params = {
            'amount': order.amount_total,
            'note': 'Order #{}'.format(order.name),
            'first_name': order.partner_id.firstname,
            'last_name': order.partner_id.lastname,
            'email': order.partner_id.email,
            'phone': order.partner_id.phone,
            'return_url': '/payment/process',
            'cancel_url': '/shop/payment',
            'webhook_url': '/payment/paymee/webhook',
            'order_id': order.name
        }

        paymee_response = paymee_acquirer.paymee_send_payment(paymee_params)

        return request.redirect(paymee_response.get('payment_url', '/shop'))

    @http.route('/payment/paymee/webhook', type='http', auth='public', csrf=False)
    def paymee_webhook(self, **post):
        paymee_acquirer = request.env['payment.acquirer'].search([('provider', '=', 'paymee')], limit=1)
        if not paymee_acquirer:
            return 'ERROR'

        response_token = post.get('token', '')
        response_payment_status = post.get('payment_status', False)
        response_order_id = post.get('order_id', '')
        response_amount = float(post.get('amount', '0.0'))
        response_received_amount = float(post.get('received_amount', '0.0'))
        response_cost = float(post.get('cost', '0.0'))
        response_check_sum = post.get('check_sum', '')

        check_sum = response_token + str(int(response_payment_status)) + paymee_acquirer.paymee_token

        if response_check_sum == check_sum:
            order = request.env['sale.order'].sudo().search([('name', '=', response_order_id)])
            if order:
                if response_payment_status:
                    payment = order.payment_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
                    payment.write({
                        'state': 'done',
                        'amount': response_received_amount,
                        'payment_transaction_id': response_token,
                    })
                    order.action_confirm()
                    return request.redirect('/shop/payment/validate')
                else:
                    payment = order.payment_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
                    payment.write({
                        'state': 'cancel',
                        'amount': response_amount,
                        'payment_transaction_id': response_token,
                    })
                    order.action_draft()

        return 'OK'
