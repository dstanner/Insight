from vector_search import vector_search
from vector_search import model_mapping
from vector_search import lookup_functions
from vector_search.model_mapping import master_dict

inds, dists, boxes = model_mapping.retrieve_img_data('1.jpg')
foo = lookup_functions.return_output(inds)
foo
choices = lookup_functions.get_choices(foo)
choices
recipe = lookup_functions.get_recipe(choices)
recipe
name, insts, table = lookup_functions.format_recipe(recipe)
table
