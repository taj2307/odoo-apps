from odoo import Command, models, fields, api, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    can_merge_partners = fields.Boolean(
        string='Can Merge Partners',
        compute='_compute_can_merge_partners',
        inverse='_inverse_can_merge_partners',
    )

    def _compute_can_merge_partners(self):
        merge_group = self.env.ref(
            'taj_partner_merge.group_partner_merge_user',
            raise_if_not_found=False,
        )
        for user in self:
            user.can_merge_partners = (
                merge_group in user.group_ids if merge_group else False
            )

    def _inverse_can_merge_partners(self):
        merge_group = self.env.ref(
            'taj_partner_merge.group_partner_merge_user',
            raise_if_not_found=False,
        )
        if not merge_group:
            return
        for user in self:
            if user.can_merge_partners:
                user.sudo().write({'group_ids': [Command.link(merge_group.id)]})
            else:
                user.sudo().write({'group_ids': [Command.unlink(merge_group.id)]})


class PartnerMergeCheck(models.TransientModel):
    _name = 'partner.merge.check.wizard'
    _description = 'Partner Merge Pre-Check'

    partner_ids = fields.Many2many('res.partner', string='Partners to Merge')
    warning_message = fields.Text(string='Warning', readonly=True)
    has_draft_invoices = fields.Boolean(readonly=True)
    draft_invoice_details = fields.Text(string='Draft Invoice Details', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])

        if len(active_ids) < 2:
            raise UserError(_('Please select at least 2 partners to merge.'))

        partners = self.env['res.partner'].browse(active_ids)
        res['partner_ids'] = [(6, 0, active_ids)]

        draft_moves = self.env['account.move'].search([
            ('partner_id', 'in', active_ids),
            ('state', '=', 'draft'),
            ('move_type', 'in', [
                'out_invoice', 'out_refund',
                'in_invoice', 'in_refund',
            ]),
        ])

        if draft_moves:
            res['has_draft_invoices'] = True
            lines = []
            for partner in partners:
                partner_drafts = draft_moves.filtered(
                    lambda m: m.partner_id.id == partner.id
                )
                if partner_drafts:
                    lines.append(f'• {partner.name}:')
                    for move in partner_drafts:
                        move_type_label = dict(
                            move._fields['move_type'].selection
                        ).get(move.move_type, move.move_type)
                        lines.append(
                            f'    - [{move_type_label}] {move.name or "/"} '
                            f'({move.currency_id.symbol or ""}'
                            f'{move.amount_total:,.2f})'
                        )
            res['draft_invoice_details'] = '\n'.join(lines)
            res['warning_message'] = (
                'The following partners have unposted (draft) invoices or bills.\n'
                'Merging with draft invoices can cause journal sequence conflicts.\n\n'
                'Please POST or DELETE these invoices before merging.'
            )
        else:
            res['has_draft_invoices'] = False
            res['warning_message'] = (
                'No draft invoices found. Safe to proceed with merge.\n\n'
                'Reminder:\n'
                '• Select the destination partner (the one to keep)\n'
                '• All invoices, payments, orders will be reassigned\n'
                '• Duplicate partners will be archived after merge'
            )

        return res

    def action_proceed_to_merge(self):
        if self.has_draft_invoices:
            raise UserError(
                _('Cannot merge. Please resolve all draft invoices first.')
            )
        return {
            'type': 'ir.actions.act_window',
            'name': _('Merge Partners'),
            'res_model': 'base.partner.merge.automatic.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_ids': self.partner_ids.ids,
                'active_model': 'res.partner',
            },
        }
