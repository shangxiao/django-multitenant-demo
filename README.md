# django-multitenant-demo

## Synopsis

Enforce shared tenancy at the database-level with foreign key constraints.

#### Model definition

```python
class Tenant(models.Model):
    ...

class TenantModel(models.Model):
    tenant_id = models.ForeignKey(Tenant)

    class Meta:
        abstract = True
        unique_together = ('id', 'tenant_id')

class TenantForeignKey(models.ForeignKey):
    # used for patching Django's schema editor to add tenant_id to fks

class Foo(TenantModel):
    ...

class Bar(TenantModel):
    foo = TenantForeignKey(Foo)
```

#### Model usage

```python
tenant_a = Tenant.objects.create(name="Tenant A")
tenant_b = Tenant.objects.create(name="Tenant B")

foo_a = Foo.objects.create(tenant=tenant_a)
bar_a = Bar.objects.create(tenant=tenant_a, foo=foo_a)

foo_b = Foo.objects.create(tenant=tenant_b)
bar_b = Bar.objects.create(tenant=tenant_b, foo=foo_a)

IntegrityError: insert or update on table "bar" violates foreign key constraint "bar_foo_id_25906a95_fk_foo_id"
DETAIL:  Key (foo_id, tenant_id)=(1, 4) is not present in table "foo".
```


## Description

Shared tenancy can be managed by the use of composite foreign keys to include _tenant-id_ in the constraint in order to
**enforce _tenant-id_ equality amongst peer models**.

There are 4 steps to this approach:

 1. Create a model `Tenant` to hold the tenant
 2. Add a `tenant_id` foreign key to to each tenancy model
 3. Add a unique constraint `(pk, tenant_id)` to each tenancy model to form a key that foreign keys can target
 4. Add the column `tenant_id` to each foreign key between tenancy models

Steps 1-3 are supported by Django but 4 requires some more work. This can be done in 2 ways:

 1. With manual migrations to include additional fk constraints on top of Django's with no intereference in the
    way Django runs things; or
 2. By patching Django's schema editor to include `tenant_id` when it generates the foreign key SQL.

#### Demonstration

This demonstration shows that with a couple of utility classes `TenantModel` and `TenantForeignKey` along with some
patching to Django's schema editor, we can easily define tenancy models with little difference to standard Django
models.

To model your database within a tenant, subclass from `TenantModel` and define any
relationships between tenant models with `TenantForeignKey`.

#### Testing is Essential

Since we may be talking about security critical modelling and the layers of abstraction that obscure implementation
details, it's always a good idea to write unit tests that check cross-tenancy relationships are rejected. See
[tests.py](app/tests.py) for an example.

#### Note

One may be tempted to discard `TenantForeignKey` and simply detect whether a foreign key
targets a tenant model during migration within the patched schema editor, however 2 things
prevent this:

 * Django renders models as "fake" models that inherit from `ModelBase` directly,
   preventing any checks for `TenantModel` type. Checking for a `tenant_id` is also
   unreliable due to the possibility that foreign keys are often split from the initial
   model state in order to satisfy migration dependencies.
 * It's possible that a model be subclassed from `TenantModel` after initially being
   migrated as a regular model. The necessary migration needed to update the foreign keys
   would not be detected in this case.

#### Patching Django

Although Django does not support composite keys out-of-the-box, there is some _partial_ support for composite keys.

Django's schema editors can add foreign keys in 2 ways:

1. The base schema editor defines method for adding foreign keys after initial table creation with _alter table_
   statements. This way _almost_ supports composite key creation. It makes use of `Column` objects that will happily
   render multiple columns and interpolates that into the foreign key creation template just fine. However it forces the
   use of a single column on both sides of the key – it's this minor update to retrieve multiple columns from a
   customised Django ForeignKey that allows us to create the required constraints.
2. The database-specific schema editors optionally define syntax for column-level (Django refers to these as "inline")
   constraints for both `CreateTable` and `AddField` operations.  Only table-level constraints support composite key
   creation and Django does not have this ability for foreign keys. This needs to be disabled in order to force the
   first way to be used.

#### Using SETTINGS instead of Monkey-Patching

This demonstration monkey-patches Django to achieve this but it is possible to do it without resorting to
monkey-patching: Schema editors can be defined for specific database backends which are an extension point with Django.
We could simply extend Django's PostgreSQL backend & schema editor classes and specify these in our `DATABASES` setting.

#### Patching for Table-Level Constraints at Create Table Time + Auto Migration Operation Ordering Issues

Using the patch from above, Django adds the foreign keys at the end of the migration – meaning that any data added in
between will not be checked for constraint integrity rather failing during foreign key creation. If constraint
definition at _create table_ time is more desirable then patching the schema editor's `table_sql()` method to add the
table-level constraints could be possible. However this could mean that the auto-generated migration operations could
fail unless manually ordered:

As you can see from the auto-generated migration file, models may have foreign keys added after the initial create table
operation. This can lead to situations where a `TenantForeignKey` has either source or target that does not yet have its
tenant-id. [Eg `CreateModel()` for `Vendor` has a foreign key to `Level` that doesn't have a foreign
key.](https://github.com/shangxiao/django-multitenant-demo/blob/master/app/migrations/0001_initial.py#L83)

#### Database Support

This demo shows how to work with PostgreSQL but should also theoretically work with MySQL as it supports foreign keys
targeting unique constraints.

SQLite support will require a bit more patching within Django. SQLite does not support adding foreign keys with alter
table statements – only within the create table statement. This would require patching `table_sql()` as mentioned above.

#### More Possible Utilities

 * Define tenant relationships for `OneToOneField` and `ManyToManyField`
 * Define a check that errors if a `TenantForeignKey` is used and both sides of the relationship are not `TenantModel`
   types.
 * Define a check that errors if a relationships exist between `TenantModel` that is not a `TenantForeignKey`
 * Define a custom manager for `TenantModel` that restricts fetching to the allowed tenants depending on the user type
 * Setup the ability to select a tenant and store in the session
