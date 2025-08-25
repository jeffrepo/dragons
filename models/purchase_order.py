# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import logging

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tipo_compra = fields.Selection([ ('admin', 'Compra administrativa'),('proyecto', 'Compra proyecto')], string='Tipo de compra')
    estado_autorizado = fields.Selection([('esperando_solicitud_aut','Esperando solicitud autorizacion'),('solicitud_aut','Solicitar autorizacion') ,('admin', 'Autorizado admin'),('aut_pago', 'Autorizacion pago'),('pago_autorizado','Pago autorizad')],string='Estado autorizado')

    @api.onchange('tipo_compra')
    def _onchange_tipo_compra(self):
        for compra in self:
            if compra.tipo_compra == 'admin':
                compra.estado_autorizado = 'esperando_solicitud_aut'

    def solicitar_autorizacion_aa(self):
        group = self.env.ref('dragons.group_dragon_admin')
        self.estado_autorizado = 'solicitud_aut'
        users_in_group = group.users
        if users_in_group:
            mensaje = "Solicita autorización de compra"
            self.message_post(partner_ids=users_in_group.mapped('partner_id').ids,body= mensaje, subject="Autorizacion", email_from=False)

    def autorizar_admin(self):
        self.estado_autorizado = 'admin'
        group = self.env.ref('dragons.group_dragon_auxiliar')
        users_in_group = group.users
        if users_in_group:
            mensaje = "Autorizado"
            self.message_post(partner_ids=users_in_group.mapped('partner_id').ids,body= mensaje, subject="Autorizado", email_from=False)

    def solicitar_autorizar_pago(self):
        self.estado_autorizado = 'aut_pago'
        group = self.env.ref('dragons.group_dragon_admin')
        users_in_group = group.users
        if users_in_group:
            mensaje = "Solicitud pago"
            self.message_post(partner_ids=users_in_group.mapped('partner_id').ids,body= mensaje, subject="Solicitu pago", email_from=False)

    def autorizar_pago(self):
        self.estado_autorizado = 'pago_autorizado'
        group = self.env.ref('dragons.group_dragon_cxp')
        users_in_group = group.users
        if users_in_group:
            mensaje = "Pago autorizado"
            self.message_post(partner_ids=users_in_group.mapped('partner_id').ids,body= mensaje, subject="Pago autorizado", email_from=False)
        
    def button_confirm(self):
        res = super().button_confirm()
        for orden in self:
            if orden.tipo_compra == 'admin':
                if orden.estado_autorizado != 'admin':
                    logging.warning('retornar error')
                    raise UserError('Flujo de aprobación incompleto')
            elif orden.tipo_compra == 'proyecto':
                if orden.amount_total <= 10000:
                    group = self.env.ref('dragons.group_dragon_gestor_proyecto')
                    users_in_group = group.users
                    if self.env.user.partner_id.id not in users_in_group.mapped('partner_id').ids:
                        raise UserError('La compra solo puede ser validada por Gestor de proyecto')
                elif orden.amount_total > 10000 and orden.amount_total <= 50000:
                    group = self.env.ref('dragons.group_dragon_direccion_general')
                    users_in_group = group.users
                    if self.env.user.partner_id.id not in users_in_group.mapped('partner_id').ids:
                        raise UserError('La compra solo puede ser valida por Direccion general')
                else:
                    pass
            else:
                pass
        return res
    
    def get_delivery_time_breakdown(self):
        self.ensure_one()
        if not self.create_date or not self.date_planned:
            return " "
        
        # Convertir a zonas horarias aware si es necesario
        create_date = self.create_date
        date_planned = self.date_planned
        
        # Calcular diferencia
        difference = date_planned - create_date
        total_seconds = difference.total_seconds()
        
        # Calcular semanas, días y horas
        total_hours = total_seconds / 3600
        weeks = int(total_hours // (24 * 7))
        remaining_hours = total_hours % (24 * 7)
        days = int(remaining_hours // 24)
        hours = int(remaining_hours % 24)
        
        # Construir el resultado
        result = []
        if weeks > 0:
            result.append(f"{weeks} week{'s' if weeks != 1 else ''}")
        if days > 0:
            result.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0 or (weeks == 0 and days == 0):
            result.append(f"{hours} hour{'s' if hours != 1 else ''}")
        
        return " ".join(result) if result else "0 hours"
                
