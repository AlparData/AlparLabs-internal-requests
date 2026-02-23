# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Abastecimiento (SIM / PIM)',
    'version': '18.0.2.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Solicitudes Internas de Material (SIM) y Pedidos Internos de Material (PIM)',
    'description': """
        Módulo de gestión de abastecimiento para empresas de Ingeniería y Construcción.
        - SIM: Solicitud Interna de Material (movimiento de stock interno).
        - PIM: Pedido Interno de Material (gestión de compra externa).
        Mantiene trazabilidad total separando logística interna de compras externas.
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
        'views/sim_views.xml',
        'views/pim_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
