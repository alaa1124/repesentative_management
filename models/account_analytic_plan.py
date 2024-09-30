from odoo import _, api, fields, models


class AccountAnalyticPlanInherit(models.Model):
    _inherit = "account.analytic.plan"
    _description = "Account Analytic Plan Inherit"

    is_project = fields.Boolean()
