from django.db import models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.backends.ddl_references import Columns, Statement, Table
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.models.fields.related import ForeignObject

from .users import User


def create_fk_sql(self, model, field, suffix):
    table = Table(model._meta.db_table, self.quote_name)
    name = self._fk_constraint_name(model, field, suffix)
    # column = Columns(model._meta.db_table, [field.column], self.quote_name)
    column = Columns(model._meta.db_table, field.get_columns(), self.quote_name)
    to_table = Table(field.target_field.model._meta.db_table, self.quote_name)
    # to_column = Columns(field.target_field.model._meta.db_table, [field.target_field.column], self.quote_name)
    to_column = Columns(
        field.target_field.model._meta.db_table,
        field.get_target_columns(),
        self.quote_name,
    )
    deferrable = self.connection.ops.deferrable_sql()
    return Statement(
        self.sql_create_fk,
        table=table,
        name=name,
        column=column,
        to_table=to_table,
        to_column=to_column,
        deferrable=deferrable,
    )


BaseDatabaseSchemaEditor._create_fk_sql = create_fk_sql


# can't use inline foreign key if multiple columns!
# (todo: add immediate constraint)
DatabaseSchemaEditor.sql_create_column_inline_fk = None


def get_columns(self):
    return (self.column,)


def get_target_columns(self):
    return (self.target_field.column,)


ForeignObject.get_columns = get_columns
ForeignObject.get_target_columns = get_target_columns


class Tenant(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TenantModel(models.Model):
    """
    A base class to add a tenant id to every model, enforcing equality
    across relationships via a custom composite foreign key. Foreign keys
    may refer to any unique key.
    """

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        # key for tenant foreign keys to reference
        unique_together = ("id", "tenant_id")
        # each sub class must define an additional fk mirroring that of Django's
        # but including tenant_id


class TenantForeignKey(models.ForeignKey):
    def get_columns(self):
        return (self.column, "tenant_id")

    def get_target_columns(self):
        return (self.target_field.column, "tenant_id")

    # Nice try, but this won't work as Django meta classes operate on models during
    # instantiaton. What we really need is a way for fields to access the class they're
    # defined in when the field is instantiated.
    # def contribute_to_class(self, cls, name, private_only=False, **kwargs):
    #     super().contribute_to_class(cls, name, private_only=private_only, **kwargs)
    #     column = self.get_attname_column()
    #     reference_table = self.remote_field.model
    #     reference_column = "id"
    #     constraint_name = f"{self.name}_fk"
    #     # use django-db-constraints to affect an additional fk constraint on top of Django's ?
    #     self.model._meta.db_constraints = {
    #         constraint_name: f"FOREIGN KEY ({column}, tenant_id) REFERENCES {reference_table} ({reference_column}, tenant_id)",
    #     }


class Site(TenantModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Level(TenantModel):
    site = TenantForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.site} - {self.name}"


class Vendor(TenantModel):
    level = TenantForeignKey(Level, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TenantUser(User):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)


class VendorUser(User):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)


class ContractorUser(User):
    ...
