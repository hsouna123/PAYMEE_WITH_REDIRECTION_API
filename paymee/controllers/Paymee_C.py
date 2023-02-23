import requests
import hashlib
import hmac
import json
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class PaymeePaymentController(http.Controller):
    @http.route('/paymee_payment/process', type='http', auth="public", website=True)
    def paymee_payment_process(self, **kwargs):
        # Get the payment amount and order reference from the request
        amount = kwargs.get('amount')
        order_ref = kwargs.get('order_ref')

        # Build the payment data payload
        payload = {
            'amount': amount,
            'note': 'Order %s' % order_ref,
            'first_name': request.env.user.partner_id.firstname,
            'last_name': request.env.user.partner_id.lastname,
            'email': request.env.user.partner_id.email,
            'phone': request.env.user.partner_id.phone,
            'return_url': request.httprequest.host_url + '/paymee_payment/return',
            'cancel_url': request.httprequest.host_url + '/paymee_payment/cancel',
            'webhook_url': request.httprequest.host_url + '/paymee_payment/webhook',
            'order_id': order_ref,
        }

        # Generate the signature
        signature = self._generate_signature(payload)

        # Add the signature to the payload
        payload['signature'] = signature

        # Make the API request to Paymee
        url = 'https://sandbox.paymee.tn/api/v2/payments/create'  # Change this to live URL for production
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Token c79d9ec616b0d8f5e306bc64fc29af32c7f19320',  # Replace with your API key
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Parse the response
        data = response.json()
        payment_url = data['data']['payment_url']

        # Redirect the user to the payment page
        return request.redirect(payment_url)

    def _generate_signature(self, data):
        """
        Generates the signature for the Paymee API request.
        """
        signature_data = ''.join([str(v) for v in data.values() if v])
        secret_key = '7fd73d1165d4a4a8bb4f1d604c4b4a65c207e8e8'  # Replace with your secret key
        signature = hmac.new(secret_key.encode(), signature_data.encode(), hashlib.sha256).hexdigest()
        return signature

    def payment_paymee(self, **post):
        # Get payment details from the payment form
        amount = post.get('amount')
        note = post.get('note')
        first_name = post.get('first_name')
        last_name = post.get('last_name')
        email = post.get('email')
        phone = post.get('phone')
        return_url = post.get('return_url')
        cancel_url = post.get('cancel_url')
        webhook_url = post.get('webhook_url')
        order_id = post.get('order_id')

        # Send payment request to Paymee API
        api_key = 'c79d9ec616b0d8f5e306bc64fc29af32c7f19320'
        url = 'https://sandbox.paymee.tn/api/v2/payments/create'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Token {api_key}'}
        data = {
            'amount': amount,
            'note': note,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'return_url': return_url,
            'cancel_url': cancel_url,
            'webhook_url': webhook_url,
            'order_id': order_id,
        }
        response = requests.post(url, headers=headers, json=data)
        payment_url = response.json()['data']['payment_url']

        # Redirect user to payment page
        return http.redirect_with_hash(payment_url)
