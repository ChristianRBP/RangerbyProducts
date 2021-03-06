# Copyright 2017, Vauxoo, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, exceptions, _


def assert_xunnel_token(function):
    """Raises an user error whenever the user
    tries to manual update either providers or invoices
    without having any Xunnel Token registered in its company.
    """
    def wraper(self):
        if not self.company_id.xunnel_token:
            raise exceptions.UserError(_(
                "Your company doesn't have a Xunnel Token "
                "established. Make sure you have saved your"
                " configuration changes before trying manual sync."))
        return function(self)
    return wraper


class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    xunnel_token = fields.Char(
        related='company_id.xunnel_token',
        help="Key-like text for authentication in controllers.")
    xunnel_testing = fields.Boolean(
        help="Use Xunnel server testing?", related='company_id.xunnel_testing')
    xunnel_succes_message = fields.Text(
        help="Message for success in the configurations settings")

    @api.model
    def get_values(self):
        res = super(AccountConfigSettings, self).get_values()
        company = self.company_id
        res.update(
            xunnel_token=company.xunnel_token,
            xunnel_testing=company.xunnel_testing
        )
        return res

    @api.multi
    def set_values(self):
        res = super(AccountConfigSettings, self).set_values()
        company = self.company_id
        company.write({
            'xunnel_token': self.xunnel_token,
            'xunnel_testing': self.xunnel_testing
        })
        return res

    @api.multi
    @assert_xunnel_token
    def sync_xunnel_providers(self):
        try:
            response = self.company_id._sync_xunnel_providers()
            message = _(
                "%s banks have been synchronized.") % len(response)
            message_class = 'success'
        except exceptions.UserError as error:
            error_message = error.name or error.value
            message = _(
                "An error has occurred while"
                " synchronizing your banks: %s.") % error_message
            message_class = 'danger'
        return {
            'type': 'ir.actions.client',
            'tag': 'account_xunnel.syncrhonized_accounts',
            'name': _('Xunnel Account.'),
            'target': 'new',
            'message': message,
            'message_class': message_class,
        }
