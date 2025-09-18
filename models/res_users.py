# -*- coding: utf-8 -*-
from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    warehouse_ids = fields.Many2many(string="Almacenes", comodel_name="stock.warehouse")
    location_ids = fields.Many2many(string="Ubicaciones", comodel_name="stock.location")
    cash_diaries_ids = fields.Many2many(
        comodel_name="account.journal",
        relation="res_users_cash_journal_rel",
        column1="user_id",
        column2="journal_id",
        string="Diarios de Efectivo y otros",
    )

    def write(self, vals):
        # Lista completa de todas las reglas que hacen referencia a campos del usuario
        rules_to_disable = [
            # Reglas de stock.warehouse
            'dragons.rule_stock_warehouse_admin',
            'dragons.rule_stock_warehouse_user',
            
            # Reglas de stock.picking.type
            'dragons.rule_stock_picking_type_admin',
            'dragons.rule_stock_picking_type_user',
            
            # Reglas de stock.picking
            'dragons.rule_stock_picking_admin',
            'dragons.rule_stock_picking_user',
            
            # Reglas de stock.quant
            'dragons.rule_stock_quant_admin',
            'dragons.rule_stock_quant_user',
            
            # Reglas de stock.move.line
            'dragons.rule_stock_move_line_admin',
            'dragons.rule_stock_move_line_user',
            
            # Reglas de account.journal
            'dragons.rule_account_journal_admin',
            'dragons.rule_some_account_journal_user',
            
            # Reglas de account.payment
            'dragons.rule_account_payment_admin',
            'dragons.rule_account_journal_user',
        ]
        
        # Guardar estado original de las reglas y desactivarlas
        original_states = {}
        for rule_xml_id in rules_to_disable:
            rule = self.env.ref(rule_xml_id, raise_if_not_found=False)
            if rule:
                original_states[rule_xml_id] = rule.active
                rule.active = False
                # Debug: verificar que se está desactivando
                print(f"Regla {rule_xml_id} desactivada: {not rule.active}")
        
        try:
            # Ejecutar el write original
            result = super().write(vals)
            
            # Reactivar las reglas a su estado original
            for rule_xml_id, original_active in original_states.items():
                rule = self.env.ref(rule_xml_id, raise_if_not_found=False)
                if rule and original_active:
                    rule.active = True
                    # Debug: verificar que se está reactivando
                    print(f"Regla {rule_xml_id} reactivada: {rule.active}")
                    
            return result
        except Exception as e:
            # En caso de error, reactivar las reglas antes de relanzar la excepción
            for rule_xml_id, original_active in original_states.items():
                rule = self.env.ref(rule_xml_id, raise_if_not_found=False)
                if rule and original_active:
                    rule.active = True
                    print(f"Regla {rule_xml_id} reactivada por error: {rule.active}")
            raise e

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_move_sms_validation = fields.Boolean(
        string="SMS Validation for Stock Moves",
        config_parameter='stock_move_sms_validation'
    )