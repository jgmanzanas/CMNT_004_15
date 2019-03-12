# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    risk_circulating_include = fields.Boolean(
        string='Include Circulating amount')
    risk_circulating_limit = fields.Monetary(
        string='Limit In Circulating amount', help='Set 0 if it is not locked')
    risk_circulating = fields.Monetary(
        compute='_compute_risk_circulating',
        string='Total Circulating amount',
        help='Total amount of circulating accounts')

    @api.model
    def _risk_field_list(self):
        res = super()._risk_field_list()
        res.append(
            ('risk_circulating_include', 'risk_circulating_limit',
             'risk_circulating'))
        return res

    def _compute_risk_circulating(self):
        for partner in self:
            move_amount_curr = self.env['account.move.line'].read_group(
                [('partner_id', 'child_of', partner.id),
                 ('account_id.circulating', '=', True),
                 ('currency_id', '!=', False),
                 ('reconciled', '=', False)],
                ['amount_residual_currency'],
                groupby='amount_residual_currency')
            move_amount = self.env['account.move.line'].read_group(
                [('partner_id', 'child_of', partner.id),
                 ('account_id.circulating', '=', True),
                 ('currency_id', '=', False),
                 ('reconciled', '=', False)],
                ['amount_residual'],
                groupby='amount_residual')
            total_amount = 0
            if move_amount_curr:
                total_amount += move_amount_curr[0]['amount_residual_currency']
            if move_amount:
                total_amount += move_amount[0]['amount_residual']
            if move_amount or move_amount_curr:
                partner.risk_circulating = total_amount
            else:
                partner.risk_circulating = 0.0
