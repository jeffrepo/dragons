# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tipo_compra = fields.Selection([ ('admin', 'Compra administrativa'),('proyecto', 'Compra proyecto')], string='Tipo de compra')
    estado_autorizado = fields.Selection([('esperando_solicitud_aut','Esperando solicitud autorizacion'),
                                          ('solicitud_aut','Solicitar autorizacion') ,('admin', 'Autorizado admin'),
                                          ('aut_pago', 'Autorizacion pago'),
                                          ('pago_autorizado','Pago autorizad'),
                                          ('firma_gestor_proyecto','Firma gestor proyecto'),
                                         ('solicitud_firma_jefep','Solicitud firma jefe proyecto'),
                                          ('solicitud_firma_op','Solicitud firma direccion operaciones'),
                                         ('solicitud_firma_legal','Solicitud firma direccion legal'),
                                          ('solicitud_firma_direccion_admin','Solicitud firma direccion administrativa'),
                                         ('solicitud_firma_direccion_general','Solicitud firma direccion general'),
                                         ('direccion_general_firmado','Direccion general firmado')],string='Estado autorizado')

    @api.onchange('tipo_compra')
    def _onchange_tipo_compra(self):
        for compra in self:
            if compra.tipo_compra == 'admin':
                compra.estado_autorizado = 'esperando_solicitud_aut'
            if compra.tipo_compra == 'proyecto':
                compra.estado_autorizado = 'firma_gestor_proyecto'

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

    def firma_gestor_proyecto(self):
        group = self.env.ref('dragons.group_dragon_gestor_proyecto')
        group_jefe = self.env.ref('dragons.group_dragon_jefe_proyecto')
        users_in_group_gestor = group.users
        users_in_group_jefe = group_jefe.users
        if self.env.user.partner_id.id in users_in_group_gestor.mapped('partner_id').ids:
            self.estado_autorizado = 'solicitud_firma_jefep'
            mensaje = "Solicitud de firma"
            self.message_post(partner_ids=users_in_group_jefe.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)
        else:
            raise UserError('No tiene permiso para firmar')

    def firma_jefe_proyecto(self):
        group = self.env.ref('dragons.group_dragon_jefe_proyecto')
        group_dir = self.env.ref('dragons.group_dragon_direccion_operaciones')
        users_in_group_gestor = group.users
        users_in_group_dir = group_dir.users
        if self.env.user.partner_id.id in users_in_group_gestor.mapped('partner_id').ids:
            self.estado_autorizado = 'solicitud_firma_op'
            mensaje = "Solicitud de firma"
            self.message_post(partner_ids=users_in_group_dir.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)
        else:
            raise UserError('No tiene permiso para firmar')

    def firma_direccion_operaciones(self):
        group = self.env.ref('dragons.group_dragon_direccion_operaciones')
        group_legal = self.env.ref('dragons.group_dragon_direccion_legal')
        users_in_group_oper = group.users
        users_in_group_legal = group_legal.users
        if self.env.user.partner_id.id in users_in_group_oper.mapped('partner_id').ids:
            self.estado_autorizado = 'solicitud_firma_legal'
            mensaje = "Solicitud de firma"
            self.message_post(partner_ids=users_in_group_legal.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)
        else:
            raise UserError('No tiene permiso para firmar')

    def firma_direccion_legal(self):
        group = self.env.ref('dragons.group_dragon_direccion_legal')
        group_gen = self.env.ref('dragons.group_dragon_direccion_admin')
        users_in_group_admin = group.users
        users_in_group_gen = group_gen.users
        if self.env.user.partner_id.id in users_in_group_admin.mapped('partner_id').ids:
            self.estado_autorizado = 'solicitud_firma_direccion_admin'
            mensaje = "Solicitud de firma"
            self.message_post(partner_ids=users_in_group_gen.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)
        else:
            raise UserError('No tiene permiso para firmar')

    def firma_direccion_admin(self):
        group = self.env.ref('dragons.group_dragon_direccion_admin')
        group_gen = self.env.ref('dragons.group_dragon_direccion_general')
        users_in_group_admin = group.users
        users_in_group_gen = group_gen.users
        if self.env.user.partner_id.id in users_in_group_admin.mapped('partner_id').ids:
            self.estado_autorizado = 'solicitud_firma_direccion_general'
            mensaje = "Solicitud de firma"
            self.message_post(partner_ids=users_in_group_gen.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)
        else:
            raise UserError('No tiene permiso para firmar')

    def firma_direccion_general(self):
        group = self.env.ref('dragons.group_dragon_direccion_general')
        users_in_group_gen = group.users
        if self.env.user.partner_id.id in users_in_group_gen.mapped('partner_id').ids:
            self.estado_autorizado = 'direccion_general_firmado'
            mensaje = "Orden de compra autorizada"
            self.message_post(partner_ids=users_in_group_gen.mapped('partner_id').ids,body= mensaje, subject="Firmar documento", email_from=False)
        else:
            raise UserError('No tiene permiso para firmar')
    
    def button_confirm(self):
        res = super().button_confirm()
        for orden in self:
            if orden.tipo_compra == 'admin':
                if orden.estado_autorizado not in ['admin','aut_pago','pago_autorizado']:
                    logging.warning('retornar error')
                    raise UserError('Flujo de aprobación incompleto')
            elif orden.tipo_compra == 'proyecto':
                if orden.estado_autorizado != 'direccion_general_firmado':
                   raise UserError('No se puede confirmar, hasta terminar el flujo de autorizaciones')
                else:
                    group = self.env.ref('dragons.group_dragon_direccion_general')
                    users_in_group_gen = group.users
                    if self.env.user.partner_id.id not in users_in_group_gen.mapped('partner_id').ids:
                        raise UserError('Solo puede confirmar direccion general')
                    else:
                        pass
            else:
                pass
        return res
                
