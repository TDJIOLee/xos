from types import StringTypes
import re
from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import SitePrivilege
from plstackapi.core.api.users import _get_users
from plstackapi.core.api.sites import _get_sites
from plstackapi.core.api.roles import _get_roles


def _get_site_privileges(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        site_privileges = SitePrivilege.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        site_privileges = SitePrivilege.objects.filter(name=filter)
    elif isinstance(filter, dict):
        site_privileges = SitePrivilege.objects.filter(**filter)
    else:
        site_privileges = []
    return site_privileges
 
def add_site_privilege(auth, fields):
    driver = OpenStackDriver(client = auth_check(auth))
    users = _get_user(fields.get('user')) 
    sites = _get_slice(fields.get('site')) 
    roles = _get_role(fields.get('role'))
    
    if users: fields['user'] = users[0]     
    if slices: fields['site'] = sites[0] 
    if roles: fields['role'] = roles[0]
 
    site_privilege = SitePrivilege(**fields)

    # update nova role
    driver.add_user_role(site_privilege.user.user_id, 
                         site_privilege.site.tenant_id, 
                         site_privilege.role.name)
    
    site_privilege.save()
    return site_privilege

def update_site_privilege(auth, id, **fields):
    return  

def delete_site_privilege(auth, filter={}):
    driver = OpenStackDriver(client = auth_check(auth))   
    site_privileges = _get_site_privileges(filter)
    for site_privilege in site_privileges:
        driver.delete_user_role(user_id=site_privilege.user.id,
                                tenant_id = site_privilege.site.tenant_id,
                                role_name = site_privilege.role.name) 
        site_privilege.delete()
    return 1

def get_site_privileges(auth, filter={}):
    client = auth_check(auth)
    users = _get_users(filter.get('user'))
    sites = _get_slices(filter.get('site'))
    roles = _get_roles(filter.get('role'))

    if users: filter['user'] = users[0]
    if sites: filter['site'] = sites[0]
    if roles: filter['role'] = roles[0]
    
    site_privileges = _get_site_privileges(filter)
    return site_privileges             
        

    