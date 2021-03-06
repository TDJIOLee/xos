from django.db import models
from core.models import PlCoreBase,SingletonModel
from core.models.plcorebase import StrippedCharField

class Service(PlCoreBase):
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Service")
    enabled = models.BooleanField(default=True)
    name = StrippedCharField(max_length=30, help_text="Service Name")
    versionNumber = StrippedCharField(max_length=30, help_text="Version of Service Definition")
    published = models.BooleanField(default=True)
    view_url = StrippedCharField(blank=True, null=True, max_length=1024)
    icon_url = StrippedCharField(blank=True, null=True, max_length=1024)

    def __unicode__(self): return u'%s' % (self.name)

class ServiceAttribute(PlCoreBase):
    name = models.SlugField(help_text="Attribute Name", max_length=128)
    value = StrippedCharField(help_text="Attribute Value", max_length=1024)
    service = models.ForeignKey(Service, related_name='serviceattributes', help_text="The Service this attribute is associated with")


