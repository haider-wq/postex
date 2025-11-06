from odoo import api, models, _, fields

class ProductFormula(models.Model):
    _name = 'product.formula'
    _rec_name = 'name'

    name = fields.Char()
    product_ingredients_line_ids = fields.One2many('product.ingredients.line', 'product_formula_link_id')



    product_ids = fields.One2many(
        'product.template',
        'product_formula_id',
        string="Linked Products"
    )

    # @api.model
    # def create(self, vals):
    #     template = super().create(vals)
    #     template._sync_bom_from_components()
    #     return template

    def write(self, vals):
        res = super().write(vals)
        self._sync_bom_from_components()
        return res

    def _sync_bom_from_components(self):
        for template in self.product_ids:

            bom = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=',template.id),
                ('type', '=', 'normal')
            ], limit=1)

            if not bom:
                product = template.product_variant_id
                bom = self.env['mrp.bom'].create({
                    'product_tmpl_id': template.id,
                    'product_id': product.id,
                    'type': 'normal',
                    # 'bom_line_ids': [(5, 0, 0)]
                })
            bom.bom_line_ids.unlink()

            # Prepare new BoM lines
            bom_lines = []

            # Add lines from product_component_line_ids
            seen_product_ids = set()
            for component in template.product_component_line_ids:
                if component.product_component_id and component.product_id:
                    if component.product_id.id not in seen_product_ids:
                        bom_lines.append((0, 0, {
                            'product_id': component.product_id.id,
                            'product_qty': component.product_qty,
                        }))
                        seen_product_ids.add(component.product_id.id)

            # Add lines from formula ingredients
            if template.product_formula_id:
                print(template.fill_weight)
                for ingredient in template.product_formula_id.product_ingredients_line_ids:
                    if ingredient.product_ingredient_id and ingredient.product_ingredient_id.id not in seen_product_ids:
                        bom_lines.append((0, 0, {
                            'product_id': ingredient.product_ingredient_id.id,
                            'product_qty': round(ingredient.product_weight_percentage * template.fill_weight /1000,7),
                        }))
                        seen_product_ids.add(ingredient.product_ingredient_id.id)

            # Write fresh BoM lines
            if bom_lines:
                bom.write({
                    'bom_line_ids': bom_lines
                })




class ProductFormula(models.Model):
    _name = 'product.ingredients.line'

    product_ingredient_id = fields.Many2one('product.product')
    product_weight_percentage = fields.Float()
    product_composition = fields.Char()
    product_formula_link_id = fields.Many2one('product.formula')



