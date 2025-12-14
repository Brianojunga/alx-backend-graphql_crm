from graphene_django import DjangoObjectType
from crm.models import Customer, Product, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields ='__all__'

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
