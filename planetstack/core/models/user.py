import os
import datetime
from collections import defaultdict
from django.db import models
from django.db.models import F, Q
from core.models import PlCoreBase,Site
from core.models.deployment import Deployment
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from timezones.fields import TimeZoneField

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=UserManager.normalize_email(email),
            firstname=firstname,
            lastname=lastname,
            password=password
        )
        #user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,
            firstname=firstname,
            lastname=lastname
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):

    class Meta:
        app_label = "core"

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True,
    )

    username = models.CharField(max_length=255, default="Something" )

    firstname = models.CharField(help_text="person's given name", max_length=200)
    lastname = models.CharField(help_text="person's surname", max_length=200)

    phone = models.CharField(null=True, blank=True, help_text="phone number contact", max_length=100)
    user_url = models.URLField(null=True, blank=True)
    site = models.ForeignKey(Site, related_name='users', help_text="Site this user will be homed too", null=True)
    public_key = models.TextField(null=True, blank=True, max_length=1024, help_text="Public key string")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_readonly = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    enacted = models.DateTimeField(null=True, default=None)
    backend_status = models.CharField(max_length=140,
                                      default="Ok")

    timezone = TimeZoneField()

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    def isReadOnlyUser(self):
        return self.is_readonly

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    @property
    def keyname(self):
        return self.email[:self.email.find('@')]

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def is_superuser(self):
        return False

#    def get_roles(self):
#        from core.models.site import SitePrivilege
#        from core.models.slice import SliceMembership
#
#        site_privileges = SitePrivilege.objects.filter(user=self)
#        slice_memberships = SliceMembership.objects.filter(user=self)
#        roles = defaultdict(list)
#        for site_privilege in site_privileges:
#            roles[site_privilege.role.role_type].append(site_privilege.site.login_base)
#        for slice_membership in slice_memberships:
#            roles[slice_membership.role.role_type].append(slice_membership.slice.name)
#        return roles   

    def save(self, *args, **kwds):
        if not self.id:
            self.set_password(self.password)    
        self.username = self.email
        super(User, self).save(*args, **kwds)  

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = User.objects.all()
        else:
            # can see all users at any site where this user has pi role
            from core.models.site import SitePrivilege
            site_privs = SitePrivilege.objects.filter(user=user)
            sites = [sp.site for sp in site_privs if sp.role.role == 'pi']
            # get site privs of users at these sites
            site_privs = SitePrivilege.objects.filter(site__in=sites)
            user_ids = [sp.user.id for sp in site_privs] + [user.id] 
            qs = User.objects.filter(Q(site__in=sites) | Q(id__in=user_ids))
        return qs            

             
    
class UserDeployments(PlCoreBase):
    user = models.ForeignKey(User)
    deployment = models.ForeignKey(Deployment)
    kuser_id = models.CharField(null=True, blank=True, max_length=200, help_text="Keystone user id")

    def __unicode__(self):  return u'%s %s' % (self.user, self.deployment.name)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = UserDeployments.objects.all()
        else:
            users = Users.select_by_user(user)
            qs = Usereployments.objects.filter(user__in=slices)
        return qs 
