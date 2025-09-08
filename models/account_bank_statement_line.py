# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"
    
    authorize_cash_conciliation = fields.Boolean(
        compute="_compute_authorize_cash_conciliation",
        store=False
    )

    application_status = fields.Selection([
        ('nuevo', 'Nuevo'),            # 👈 Estado inicial
        ('pendiente', 'Pendiente'),
        ('autorizado', 'Autorizado')
    ], string="Estado de la solicitud", readonly=True, default='nuevo')

    
    def _compute_authorize_cash_conciliation(self):
        for rec in self:
            rec.authorize_cash_conciliation = self.env.user.authorize_cash_conciliation
    
    
    @api.model_create_multi
    def create(self, vals_list):
        # 🔎 VALIDACIÓN ANTES DE CREAR
        for vals in vals_list:
            journal_id = vals.get("journal_id")
            
            if journal_id:
                journal = self.env["account.journal"].browse(journal_id)
                if journal.type == "cash":
                    # saldo actual
                    existing_balance = journal.current_statement_balance
                    # nuevo saldo con lo que intenta crear
                    running_balance = existing_balance + vals.get("amount", 0.0)

                    if journal.limit and running_balance > journal.limit:
                        self.env.cr.commit()
                        lines = self.env['account.bank.statement.line'].search([('application_status', '=', 'nuevo')])
                        for line in lines:
                            line.unlink()
                            self.env.cr.commit()
                        raise UserError(
                            "😬 Esta conciliación no se podrá permitir, "
                            "se ha llegado al límite del diario"
                        )

        # 🔁 Si todo bien → llamar al create original
        return super(AccountBankStatementLine, self).create(vals_list)

    def action_save_close(self):
        for line in self:
            journal = line.journal_id
            if journal.type == "cash":
                # saldo actual
                existing_balance = journal.current_statement_balance
                print("save and close existing_balance ", existing_balance)
                # nuevo saldo con esta línea incluida
                running_balance = existing_balance

                if journal.limit and running_balance > journal.limit:
                    print("Save/Close Line ", line)
                    
                    # Eliminar solo la línea actual, no todas
                    line_to_delete = self.env['account.bank.statement.line'].browse(line.id)
                    if line_to_delete.exists():
                        line_to_delete.unlink()
                        self.env.cr.commit()  # Solo un commit después de eliminar
                    
                    raise UserError(
                        "😬 Esta conciliación no se podrá permitir, "
                        "se ha llegado al límite del diario"
                    ) 
        
        return super(AccountBankStatementLine, self).action_save_close()

    def action_save_new(self):
        for line in self:
            journal = line.journal_id
            if journal.type == "cash":
                # saldo actual
                existing_balance = journal.current_statement_balance
                # nuevo saldo con esta línea incluida
                running_balance = existing_balance
                print("save and new existing_balance ", existing_balance)
                
                if journal.limit and running_balance > journal.limit:
                    # Eliminar solo la línea actual
                    line_to_delete = self.env['account.bank.statement.line'].browse(line.id)
                    if line_to_delete.exists():
                        line_to_delete.unlink()
                        self.env.cr.commit()  # Solo un commit después de eliminar
                    
                    raise UserError(
                        "😬 Esta conciliación no se podrá permitir, "
                        "se ha llegado al límite del diario"
                    )

        return super().action_save_new()

    def write(self, vals):
        print("write vals ", vals)
        for rec in self:
            if rec.write_date != rec.create_date:
                print("rec.write_date " + str(rec.write_date) + " --> " + str(rec.create_date) + " create_date")
                print("before write rec.is_reconciled ", rec.is_reconciled)

                # Caso: el usuario intenta reconciliar estando pendiente
                if rec.is_reconciled and rec.application_status == 'pendiente':
                    raise UserError("😐 Aún no ha sido autorizado")

                # Caso: el usuario intenta reconciliar sin tener autorización ni estatus aprobado
                if rec.is_reconciled \
                and rec.application_status != 'autorizado' \
                and not self.env.user.authorize_cash_conciliation:
                    raise UserError("😥 Por favor solicite autorización")

            # 🔎 Validación 2: monto mayor al saldo disponible
            if "amount" in vals:
                journal = rec.journal_id
                if journal.type == "cash":
                    new_amount = vals.get("amount", rec.amount)
                    existing_balance = journal.current_statement_balance
                    running_balance = existing_balance - rec.amount + new_amount
                    print(f"[DEBUG] write check: existing={existing_balance}, old={rec.amount}, new={new_amount}, running={running_balance}")

                    if journal.limit and running_balance > journal.limit:
                        raise UserError(
                            "😬 No se puede modificar la línea: "
                            "el monto supera el saldo actual del diario"
                        )

        return super(AccountBankStatementLine, self).write(vals)

    def request_authorization(self):
        self.application_status = 'pendiente'
        return "xx"
            
    def grant_permission(self):
        self.application_status = 'autorizado'
        return "Permiso autorizado"
    
    # def return_permission(self):
    #     self.application_status = 'pendiente'
    #     return "xx"