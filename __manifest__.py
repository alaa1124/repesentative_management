{
    'name': 'Representative Management',
    'summary': 'Representative Management',
    'author': "Amr Othman",
    'company': '',
    'website': "",
    'version': '17.0',
    'category': 'Hr',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'account',
        'hr'
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/account_analytic_account.xml',
        'views/account_analytic_plan.xml',
        'views/operation_management.xml',
        'views/operation_management_line.xml',
        'views/operation_partner.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

