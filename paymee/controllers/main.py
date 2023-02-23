from odoo import http
from odoo.http import request
import hashlib


class PaymeeController(http.Controller):

    @http.route('/payment/paymee', type='http', auth='user')
    def paymee_payment(self, **post):
        # Get the partner and the order to be paid
        partner = request.env.user.partner_id
        order = request.env['sale.order'].browse(int(post.get('order_id')))

        # Prepare the data to be sent in the Paymee API request
        amount = order.amount_total
        note = 'Order #' + str(order.id)
        first_name = partner.name
        last_name = ''
        email = partner.email
        phone = partner.phone
        return_url = 'https://www.return_url.tn'
        cancel_url = 'https://www.cancel_url.tn'
        webhook_url = 'https://www.webhook_url.tn'
        order_id = str(order.id)
        api_key = 'c79d9ec616b0d8f5e306bc64fc29af32c7f19320'

        data = {
            "amount": amount,
            "note": note,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "return_url": return_url,
            "cancel_url": cancel_url,
            "webhook_url": webhook_url,
            "order_id": order_id
        }

        # Send the Paymee API request to initiate the payment
        api_url = 'https://sandbox.paymee.tn/api/v2/payments/create'
        headers = {'Content-Type': 'application/json', 'Authorization': 'Token ' + api_key}
        response = http.request.http.request(api_url, headers=headers, json=data)

        # Get the payment_url from the Paymee API response
        response_data = response.json()
        if response_data['status']:
            payment_url = response_data['data']['payment_url']

            # Redirect the user to the payment_url to complete the payment
            return http.redirect_with_hash(payment_url)

    @http.route('/payment/paymee_webhook', type='json', auth='none', csrf=False)
    def paymee_webhook(self, **post):
        # Verify the checksum to make sure the request is authentic
        token = post['token']
        payment_status = post['payment_status']
        api_key = 'your_api_key_here'

        checksum_str = token + str(int(payment_status)) + api_key
        calculated_checksum = hashlib.sha256(checksum_str.encode()).hexdigest()

        if calculated_checksum != post['check_sum']:
            return {'success': False, 'message': 'Checksum verification failed'}

        # Process the payment based on the payment_status
        if payment_status:
            # Payment successful, process the order accordingly
            order_id = post['order_id']
            amount = post['amount']
            transaction_id = post['transaction_id']
            received_amount = post['received_amount']
            cost = post['cost']

            # Find the order to update
            order = request.env['sale.order'].sudo().search([('id', '=', order_id)])

            if not order:
                return {'success': False, 'message': 'Order not found'}

            # Check that the payment amount matches the order amount
            if amount != order.amount_total:
                return {'success': False, 'message': 'Invalid payment amount'}

            # Update the order status and payment information
            order.write({
                'payment_tx_id': transaction_id,
                'payment_tx_type': 'paymee',
                'payment_tx_state': 'done',
                'payment_amount': received_amount,
                'payment_tx_fee': cost,
                'state': 'sale',
            })

        else:
            # Payment failed, handle the failure accordingly
            order_id = post['order_id']
            amount = post['amount']

            # Find the order to update
            order = request.env['sale.order'].sudo().search([('id', '=', order_id)])

            if not order:
                return {'success': False, 'message': 'Order not found'}

            # Update the order status
            order.write({
                'state': 'draft',
            })

        # Return a success response to Paymee
        return {'success': True, 'message': 'Payment status updated'}
