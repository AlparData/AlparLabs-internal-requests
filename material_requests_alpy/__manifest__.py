# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Abastecimiento (PIM)',
    'version': '18.0.3.0.4',
    'category': 'Inventory/Purchase',
    'summary': 'Pedidos Internos de Material (PIM)',
    'description': """
        Módulo de gestión de abastecimiento para empresas de Ingeniería y Construcción.
        - PIM: Pedido Interno de Material (gestión de compra externa).
    """,
    'author': 'Alpar Labs',
    'website': 'https://www.alparlabs.com',
    'depends': [
        'base',
        'mail',
        'project',
        'stock',
        'purchase',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'report/pim_report.xml',
        'wizard/pim_create_po_wizard_views.xml',
        'views/pim_views.xml',
        'views/menu_views.xml',
        'views/project_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
