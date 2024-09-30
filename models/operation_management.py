from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class OperationManagement(models.Model):
    _name = "operation.management"
    _description = "Operation Management"

    name = fields.Char(
        string="Reference"
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('invoiced', 'Invoiced'),
        ('done', 'Done'),
    ], default="draft")
    month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December')
    ], string='Month', default='1')
    date_from = fields.Date()
    date_to = fields.Date()
    partner_id = fields.Many2one(
        'operation.partner'
    )
    line_ids = fields.One2many(
        'operation.management.line',
        'operation_id'
    )
    invoice_id = fields.Many2one(
        'account.move',
        readonly=1
    )
    is_invoice_posted = fields.Boolean(
        compute='_compute_is_invoice_posted',
    )

    @api.depends('invoice_id.state')
    def _compute_is_invoice_posted(self):
        for rec in self:
            rec.is_invoice_posted = rec.invoice_id.state == 'posted'

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValidationError(_('Date From must be less than or equal to Date To.'))

    def action_in_progress(self):
        self.state = 'in_progress'

    def action_approve(self):
        self.state = 'approved'

    def action_create_invoice(self):
        lines = self.prepare_invoice_lines()
        invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'state': 'draft',
            'partner_id': self.partner_id.partner_id.id,
            'invoice_date': self.date_to,
            'invoice_date_due': self.date_to,
            'delivery_date': self.date_to,
            'journal_id': self.partner_id.journal_id.id,
            'ref': self.name,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.partner_id.product_id.id,
                'name': f"{self.name} / {lines[line]['name']} / {line}",
                'quantity': lines[line]['total_orders'],
                'analytic_distribution': {
                    lines[line]['analytic']: 100,
                    self.partner_id.cost_center_id.id : 100,
                }
            }) for line in lines.keys()]
        })
        self.invoice_id = invoice

    def prepare_invoice_lines(self):
        drivers_info = {}
        for line in self.line_ids:
            if line.driver_username not in drivers_info.keys():
                analytic_account = self.env['account.analytic.account'].sudo().search([
                    ('code', '=', line.driver_username)
                ], limit=1)
                drivers_info[line.driver_username] = {
                    'name': line.driver_name,
                    'total_orders': 1,
                    'analytic': analytic_account.id if analytic_account else False,
                }
            else:
                drivers_info[line.driver_username]['total_orders'] += 1
        return drivers_info

    def action_view_lines(self):
        return {
            'name': _('Operation Management Lines'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'operation.management.line',
            'domain': [('operation_id', '=', self.id)],
            'context': {
                'default_operation_id': self.id,
            },
        }

    def action_view_invoice(self):
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
        }



class OperationManagementLine(models.Model):
    _name = "operation.management.line"
    _description = "Operation Management Line"

    operation_id = fields.Many2one(
        'operation.management',
        readonly=1
    )
    no = fields.Integer()
    did = fields.Char(
        string="DID"
    )
    ref_id = fields.Char(
        string="Ref. ID"
    )
    driver_name = fields.Char()
    driver_username = fields.Char()
    driver_id = fields.Char(
        string="Driver ID"
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account'
    )
    amount = fields.Float()
    actual_amount = fields.Float()
    gap = fields.Float(
        compute='_compute_gap',
    )
    price = fields.Float()
    driver_debit_amount = fields.Float()
    total_debit = fields.Float(
        compute='_compute_total_debit',
    )
    driver_credit_amount = fields.Float()
    tips = fields.Float()
    blocked_amount = fields.Float()
    bonus = fields.Float(
        compute='_compute_bonus',
    )
    is_free_order = fields.Boolean()
    dispatch_time = fields.Datetime()

    @api.depends('amount', 'actual_amount')
    def _compute_gap(self):
        for rec in self:
            rec.gap = rec.amount - rec.actual_amount

    @api.depends('driver_credit_amount', 'blocked_amount', 'tips')
    def _compute_bonus(self):
        for rec in self:
            rec.bonus = rec.driver_credit_amount - (rec.blocked_amount + rec.tips)

    @api.depends('driver_debit_amount', 'gap')
    def _compute_total_debit(self):
        for rec in self:
            rec.total_debit = rec.driver_debit_amount + rec.gap

    @api.constrains('driver_username')
    def _check_driver_username(self):
        for rec in self:
            analytic = self.env['account.analytic.account'].sudo().search([
                ('code', '=', rec.driver_username),
            ], limit=1)
            rec.analytic_account_id = analytic
