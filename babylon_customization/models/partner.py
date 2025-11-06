# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_
import logging
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    contact_code = fields.Char(string='Contact Code')

    @api.constrains('contact_code')
    def _check_unique_contact_code(self):
        for record in self:
            # Search for other records with the same default_code
            existing = self.search([
                ('contact_code', '=', record.contact_code),
                ('contact_code', '!=', False)

            ])
            if len(existing) > 1:
                raise ValidationError(
                    "An Contact Name with the same Contact Code '%s' already exists." % record.contact_code)


