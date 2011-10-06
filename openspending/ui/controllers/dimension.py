import logging

from pylons import request, tmpl_context as c
from pylons.controllers.util import abort
from pylons.decorators.cache import beaker_cache
from pylons.i18n import _

from openspending import model
from openspending.ui.lib.jsonp import to_jsonp
from openspending.ui.lib.base import BaseController, render
from openspending.ui.lib.page import Page

log = logging.getLogger(__name__)

PAGE_SIZE = 100

class DimensionController(BaseController):

    @beaker_cache(invalidate_on_startup=True,
           cache_response=False,
           query_args=True)
    def index(self, dataset, format='html'):
        c.dataset = model.Dataset.by_name(dataset)
        if not c.dataset:
            abort(404, _('Sorry, there is no dataset named %s') % dataset)
        c.dimensions = c.dataset.dimensions 
        if format == 'json':
            return to_jsonp([d.as_dict() for d in c.dimensions])
        else:
            return render('dimension/index.html')

    @beaker_cache(invalidate_on_startup=True,
           cache_response=False,
           query_args=True)
    def view(self, dataset, dimension, format='html'):
        c.dataset = model.Dataset.by_name(dataset)
        if not c.dataset:
            abort(404, _('Sorry, there is no dataset named %s') % dataset)
        try:
            c.dimension = c.dataset[dimension]
        except KeyError:
            abort(400, _('This is not a dimension'))
        if not isinstance(c.dimension, model.Dimension):
            abort(400, _('This is not a dimension'))

        # TODO: pagination!
        try:
            page = int(request.params.get('page'))
        except:
            page = 1
        result = c.dataset.aggregate(drilldowns=[dimension], page=page, 
                    pagesize=PAGE_SIZE, order=[('amount', True)])
        items = result.get('drilldown', [])
        c.values = [(d.get(dimension), d.get('amount')) for d in items]

        if format == 'json':
            return to_jsonp({
                "values": c.values,
                "meta": c.dimension.as_dict()})

        c.page = Page(c.values, page=page,
                      items_per_page=PAGE_SIZE)
        return render('dimension/view.html')
