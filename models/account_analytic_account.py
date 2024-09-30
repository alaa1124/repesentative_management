from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AccountAnalyticAccountInherit(models.Model):
    _inherit = "account.analytic.account"
    _description = "Account Analytic Account Inherit"

    gahez_id = fields.Char(
        string="Gahez ID"
    )
    employee_id = fields.Many2one(
        'hr.employee',
    )

    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0 and record.code:
                raise ValidationError(_('The code must be unique.'))
