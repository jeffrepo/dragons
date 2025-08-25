# -*- coding: utf-8 -*-
{
    'name': "dragons",

    'summary': """ Funcionalidades extras para Dragons """,

    'description': """
    Funcionalidades extras para ENGATEL 
    """,

    'author': "Jefferson Silva",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'stock'],

    # always loaded
    'data': [
        'security/dragons_security.xml',
        'security/ir_rules.xml',
        'reports/order_purchase_report_pdf_view.xml',
        'reports/report_action.xml',
        'views/purchase_views.xml',
        # 'views/res_users_views.xml',
    ],
}

