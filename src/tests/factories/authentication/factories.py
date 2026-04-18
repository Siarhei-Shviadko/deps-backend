import factory
from pytest_factoryboy import register

from deps_documents.domain.entities import RoleEntity, UserAuthEntity, UserEntity


@register
class UserAuthEntityFactory(factory.Factory):
    class Meta:
        model = UserAuthEntity

    user_name = factory.Faker("email")
    password = factory.Faker("sha256")


@register
class RoleEntityFactory(factory.Factory):
    class Meta:
        model = RoleEntity

    name = factory.Faker("word")


@register
class UserEntityFactory(factory.Factory):
    class Meta:
        model = UserEntity

    pk = None
    role = None
    name = factory.Faker("user_name")
    uuid = factory.Faker("md5")
    auth_info = factory.SubFactory(UserAuthEntityFactory)
