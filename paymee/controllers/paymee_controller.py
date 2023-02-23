# This code handles the incoming request from Paymee
# and updates the state of the payment transaction accordingly based on the status of the payment.
# If the payment is successful, the transaction state is set to 'done' and the Paymee transaction ID is stored.
# If the payment is cancelled, the transaction state is set to 'cancel'.
# The code then redirects the user to the return URL specified in the payment acquirer settings.
from odoo import http
from odoo.http import request


# NECESSAIRE POUR LE PAYMEE PROVIDER ACQUIRER IN ODOO 14
# #Ce code implémente un contrôleur de paiement Paymee pour Odoo.
# Il gère les notifications de paiement en provenance de Paymee.
# Les notifications sont vérifiées, puis le statut du paiement est mis à jour.
# Si le paiement est approuvé, il est validé et une réponse 'OK' est renvoyée.

class PaymeeControllers(http.Controller):
    @http.route(['/payment/paymee/s2s'], type='http', auth='none', csrf=False)
    def paymee_s2s_return(self, **post):
        # optionel
        acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'paymee')], limit=1)
        if not acquirer_id:
            return 'No Paymee acquirer found'

        tx = request.env['payment.transaction'].sudo().search([('reference', '=', post.get('order_id'))])
        if not tx:
            return 'Transaction not found'

        status = post.get('status')
        paymee_token = post.get('paymee_token')
        if status == 'success':
            tx.write({
                'state': 'done',
                'paymee_txn_id': paymee_token
            })
        else:
            tx.write({
                'state': 'cancel',
                'paymee_txn_id': paymee_token
            })

        return_url = acquirer_id.return_url
        return request.redirect(return_url)
