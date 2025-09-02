from collections import defaultdict

import markupsafe

from odoo import Command, models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import frozendict, SQL
import logging

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    def _create_payments(self):
        logging.warning("_create_payments inherits")
        self.ensure_one()
        batches = []
        # Skip batches that are not valid (bank account not setup or not trusted but required)
        for batch in self.batches:
            batch_account = self._get_batch_account(batch)
            if self.require_partner_bank_account and (not batch_account or not batch_account.allow_out_payment):
                continue
            batches.append(batch)

        if not batches:
            raise UserError(_(
                "To record payments with %(payment_method)s, the recipient bank account must be manually validated. You should go on the partner bank account in order to validate it.",
                payment_method=self.payment_method_line_id.name,
            ))

        first_batch_result = batches[0]
        edit_mode = self.can_edit_wizard and (len(first_batch_result['lines']) == 1 or self.group_payment)
        to_process = []

        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard(first_batch_result)
            to_process_values = {
                'create_vals': payment_vals,
                'to_reconcile': first_batch_result['lines'],
                'batch': first_batch_result,
            }

            # Force the rate during the reconciliation to put the difference directly on the
            # exchange difference.
            if self.writeoff_is_exchange_account and self.currency_id == self.company_currency_id:
                total_batch_residual = sum(first_batch_result['lines'].mapped('amount_residual_currency'))
                to_process_values['rate'] = abs(total_batch_residual / self.amount) if self.amount else 0.0

            to_process.append(to_process_values)
        else:
            if not self.group_payment:
                # Don't group payments: Create one batch per move.
                lines_to_pay = self._get_total_amounts_to_pay(batches)['lines'] if self.installments_mode in ('next', 'overdue', 'before_date') else self.line_ids
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        if line not in lines_to_pay:
                            continue
                        new_batches.append({
                            **batch_result,
                            'payment_values': {
                                **batch_result['payment_values'],
                                'payment_type': 'inbound' if line.balance > 0 else 'outbound'
                            },
                            'lines': line,
                        })
                batches = new_batches

            for batch_result in batches:
                to_process.append({
                    'create_vals': self._create_payment_vals_from_batch(batch_result),
                    'to_reconcile': batch_result['lines'],
                    'batch': batch_result,
                })

        lines = sum((batch_result['lines'] for batch_result in batches), self.env['account.move.line'])
        from_sibling_companies = self._from_sibling_companies(lines)
        if from_sibling_companies and lines.company_id.root_id not in self.env.companies:
            # Payment made for sibling companies, we don't want to redirect to the payments
            # to avoid access error, as it will be created as parent company.
            self.env.context = {**self.env.context, "dont_redirect_to_payments": True}

        wizard = self.sudo() if from_sibling_companies else self

        payments = wizard._init_payments(to_process, edit_mode=edit_mode)
        #wizard._post_payments(to_process, edit_mode=edit_mode)
        #swizard._reconcile_payments(to_process, edit_mode=edit_mode)
        return payments.sudo(flag=False)