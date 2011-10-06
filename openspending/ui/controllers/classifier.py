import logging

from pylons import request, response, tmpl_context as c
from pylons.decorators.cache import beaker_cache
from pylons.controllers.util import abort
from pylons.i18n import _

from openspending import model
from openspending.plugins.core import PluginImplementations
from openspending.plugins.interfaces import IClassifierController
from openspending.ui.lib.base import BaseController, render
from openspending.ui.lib.views import handle_request
from openspending.ui.lib.helpers import url_for
from openspending.ui.lib.browser import Browser

log = logging.getLogger(__name__)


class ClassifierController(BaseController):

    extensions = PluginImplementations(IClassifierController)

    @beaker_cache(invalidate_on_startup=True,
                  cache_response=False,
                  query_args=True)
    def view(self, *args, **kwargs):
        return super(ClassifierController, self).view(*args, **kwargs)

    @beaker_cache(invalidate_on_startup=True,
                  cache_response=False,
                  query_args=True)
    def view_by_taxonomy_name(self, taxonomy, name, format="html"):
        classifier = self._filter({"taxonomy": taxonomy, "name": name})
        if not classifier:
            abort(404)
        return self._handle_get(result=classifier[0], format=format)

    @beaker_cache(invalidate_on_startup=True,
                  cache_response=False,
                  query_args=True)
    def entries(self, taxonomy, name, format='html'):
        c.classifier = model.classifier.find_one({'taxonomy': taxonomy,
                                                  'name': name})
        if not c.classifier:
            abort(404, _('Sorry, there is no such classifier'))

        self._make_browser()
        if format == 'json':
            return c.browser.to_jsonp()
        elif format == 'csv':
            c.browser.to_csv()
        else:
            return render('classifier/entries.html')

    def _view_html(self, classifier):
        c.classifier = classifier

        handle_request(request, c, c.classifier)
        if c.view is None:
            self._make_browser()

        c.num_entries = self._entry_q(c.classifier).count()
        c.template = 'classifier/view.html'

        for item in self.extensions:
            item.read(c, request, response, c.classifier)

        return render(c.template)

    def _entry_q(self, classifier):
        return model.entry.find({'classifiers': c.classifier['_id']})

    def _make_browser(self):
        url = url_for(controller='classifier', action='entries',
                taxonomy=c.classifier['taxonomy'],
                name=c.classifier['name'])
        c.browser = Browser(request.params, url=url)
        c.browser.filter_by("+classifiers:%s" % c.classifier['_id'])
        c.browser.facet_by_dimensions()
