{
    'name': 'Paymee Payment',
    'summary': 'Integration with Paymee payment gateway',
    'description': 'This module provides integration with the Paymee payment gateway with redirection for online payments.',
    'category': 'Accounting',
    'version': '1.0',
    'sequence': '-1000000',
    'author': 'BMG _ TECH _ HSOUNA ',
    # 'website': 'https://www.yourwebsite.com',
    'license': 'AGPL-3',
    'depends': ['base', 'payment', 'website', 'sale', 'website_sale'],
    'data': [
        'views/form_view.xml',
        'views/Paymee_payment_acquirer.xml',
        # 'views/paymee_template.xml',
        # 'data/payment_acquirer_data.xml',
        'security/ir.model.access.csv',
    ],
    'external_dependencies': {
        'python': [
            'requests'
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
