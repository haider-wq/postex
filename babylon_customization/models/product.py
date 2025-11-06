
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    box_size = fields.Char()
    box = fields.Integer()
    net_weight = fields.Integer()
    fill_weight = fields.Integer()
    is_ingredient = fields.Boolean(default=False)
    incl = fields.Char()
    is_component = fields.Boolean(default=False)
    form_factor = fields.Selection([('tube','TUBE') ,('bottle','BOTTLE'),('jar','JAR'),('packet','PACKET'),('buket','BUCKET')])
    product_ups_image = fields.Binary()
    case_pack_ups_image = fields.Binary()
    product_label_image = fields.Binary()
    outerbox_image = fields.Binary()
    status_tag = fields.Selection([('archived','Archived'),('production','Production')])
    product_formula_id = fields.Many2one('product.formula')
    product_component_line_ids = fields.One2many('product.components.line','product_component_id')


    @api.constrains('default_code')
    def _check_unique_default_code(self):
        for record in self:
            # Search for other records with the same default_code
            existing = self.search([
                ('default_code', '=', record.default_code),
                ('default_code', '!=',False),
                ('is_ingredient', '=', True)  # Ensure it is not the current record
            ])
            if len(existing) > 1:
                raise ValidationError("An Ingredient Name with the same Code '%s' already exists." % record.default_code)


class ProductFormula(models.Model):
    _name = 'product.components.line'

    product_id = fields.Many2one('product.product')
    uom_id = fields.Many2one("uom.uom", "Unit Of Measure")
    product_qty = fields.Float()
    product_component_id = fields.Many2one('product.template')
