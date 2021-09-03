import pytest
from django.db import IntegrityError, connection
from django.test import TestCase
from psycopg2.errors import ForeignKeyViolation

from .models import Level, Site, Tenant, Vendor

pytestmark = pytest.mark.django_db


def test_normal_tenancy():
    rialto_tenant = Tenant.objects.create(
        name="Rialto",
    )
    rialto_site = Site.objects.create(
        name="Rialto Towers",
        tenant=rialto_tenant,
    )
    rialto_level_55 = Level.objects.create(
        name="Level 55",
        site=rialto_site,
        tenant=rialto_tenant,
    )
    Vendor.objects.create(
        name="Vue de monde",
        level=rialto_level_55,
        tenant=rialto_tenant,
    )

    woolworths_tenant = Tenant.objects.create(
        name="Woolworths",
    )
    woolworths_site = Site.objects.create(
        name="Collins St Supermarker",
        tenant=woolworths_tenant,
    )
    woolworths_collins_ground_floor = Level.objects.create(
        name="Ground Floor",
        site=woolworths_site,
        tenant=woolworths_tenant,
    )
    Vendor.objects.create(
        name="Collins St Franchise",
        level=woolworths_collins_ground_floor,
        tenant=woolworths_tenant,
    )


def test_cant_cross_assign_levels():
    rialto_tenant = Tenant.objects.create(
        name="Rialto",
    )
    rialto_site = Site.objects.create(
        name="Rialto Towers",
        tenant=rialto_tenant,
    )
    woolworths_tenant = Tenant.objects.create(
        name="Woolworths",
    )

    Level.objects.create(
        name="I'm confused!",
        site=rialto_site,
        tenant=woolworths_tenant,
    )
    with pytest.raises(
        IntegrityError,
        match='insert or update on table "app_level" violates foreign key constraint',
    ):
        # check here since the removal of inline fk removed the "set constraints immediate" statement
        connection.check_constraints()


def test_cant_cross_assign_vendors():
    rialto_tenant = Tenant.objects.create(
        name="Rialto",
    )
    rialto_site = Site.objects.create(
        name="Rialto Towers",
        tenant=rialto_tenant,
    )
    rialto_level_55 = Level.objects.create(
        name="Level 55",
        site=rialto_site,
        tenant=rialto_tenant,
    )
    woolworths_tenant = Tenant.objects.create(
        name="Woolworths",
    )

    Vendor.objects.create(
        name="I'm confused!",
        level=rialto_level_55,
        tenant=woolworths_tenant,
    )
    with pytest.raises(
        IntegrityError,
        match='insert or update on table "app_vendor" violates foreign key constraint',
    ):
        # check here since the removal of inline fk removed the "set constraints immediate" statement
        connection.check_constraints()
