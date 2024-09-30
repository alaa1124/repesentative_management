from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class OperationPartner(models.Model):
    _name = "operation.partner"
    _description = "Operation Partner"

    name = fields.Char(
        required=True,
    )
    product_id = fields.Many2one(
        'product.product'
    )
    journal_id = fields.Many2one(
        'account.journal',
        domain="[('type', '=', 'sale')]"
    )
    cost_center_id = fields.Many2one(
        'account.analytic.account',
        domain="[('plan_id.is_project', '=', True)]"
    )
    partner_id = fields.Many2one(
        'res.partner'
    )


