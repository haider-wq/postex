# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_
import logging
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class InheritedMrpBom(models.Model):
    _inherit = "mrp.bom"
    product_name = fields.Char(related='product_tmpl_id.name')



