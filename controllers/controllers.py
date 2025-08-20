# -*- coding: utf-8 -*-
# from odoo import http


# class L10nGtDragons(http.Controller):
#     @http.route('/l10n_gt_dragons/l10n_gt_dragons', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_gt_dragons/l10n_gt_dragons/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_gt_dragons.listing', {
#             'root': '/l10n_gt_dragons/l10n_gt_dragons',
#             'objects': http.request.env['l10n_gt_dragons.l10n_gt_dragons'].search([]),
#         })

#     @http.route('/l10n_gt_dragons/l10n_gt_dragons/objects/<model("l10n_gt_dragons.l10n_gt_dragons"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_gt_dragons.object', {
#             'object': obj
#         })

