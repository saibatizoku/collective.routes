# -*- encoding: utf-8 -*-

from Acquisition import aq_inner
from five import grok
from zope import schema
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements
from zope.interface import Interface
from zope.site.hooks import getSite

from Products.CMFCore.utils import getToolByName
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRecordModifiedEvent
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from collective.routes import getRoute
from collective.routes import getRouteNames
from collective.routes import getObject
from collective.routes import _


class RoutesVocabulary(object):
    """Creates a vocabulary with all the routes available on the
    site.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = []
        for route_name in getRouteNames():
            route = getRoute(route_name)
            if not route:
                continue
            items.append(SimpleVocabulary.createTerm(route.name,
                                                     route.name,
                                                     route.name))
        return SimpleVocabulary(items)

grok.global_utility(RoutesVocabulary,
                    name=u'collective.routes.Routes')


class IRoutesSettings(Interface):
    """ Interface describing the settings on the control panel """
    routes = schema.Set(
            title=_(u"Available Routes"),
            description=_(u""),
            value_type=schema.Choice(vocabulary=u"collective.routes.Routes"),
            default=set([]),
            missing_value=set([]),
            required=False,
            )


class RoutesSettingsEditForm(controlpanel.RegistryEditForm):
    schema = IRoutesSettings
    label = _(u'Routes Settings')
    description = _(u'Here you can modify the settings for '
                     'Routes.')
    def updateFields(self):
        super(RoutesSettingsEditForm, self).updateFields()
        self.fields['routes'].widgetFactory = CheckBoxFieldWidget

    def updateWidgets(self):
        super(RoutesSettingsEditForm, self).updateWidgets()


class RoutesConfiglet(controlpanel.ControlPanelFormWrapper):
    form = RoutesSettingsEditForm


@grok.subscribe(IRoutesSettings, IRecordModifiedEvent)
def detectRoutesChange(settings, event):
    if event.record.fieldName == 'routes':
        context = aq_inner(settings)
        pprops = getToolByName(context, 'portal_properties')
        route_props = pprops.routes_properties
        route_props.activated_routes = tuple(event.newValue)
