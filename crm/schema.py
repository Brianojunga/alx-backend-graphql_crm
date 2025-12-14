import graphene
from graphene import List, Field
from django.db import transaction
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from .types import CustomerType, ProductType, OrderType

class CRMQuery(graphene.ObjectType):
    hello = graphene.String(default_value = 'Hello, GraphQl')


class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise ValidationError('Email already exists.')

        customer = Customer(
            name=name,
            email=email,
            phone=phone
        )
        customer.save()

        return CreateCustomer(
            customer=customer,
            message="Customer created successfully.",
            success=True
        )
    
#Bulk create customers
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCreateCustomers(graphene.Mutation):
    customers = List(CustomerType)
    errors = List(graphene.String)

    class Arguments:
        customers = List(CustomerInput, required=True)

    def mutate(self, info, customers):
        created = []
        errors = []

        with transaction.atomic():
            for index, data in enumerate(customers):
                try:
                    if Customer.objects.filter(email=data.email).exists():
                        raise ValidationError("Email already exists")


                    customer = Customer.objects.create(
                            name=data.name,
                            email=data.email,
                            phone=data.phone
                        )
                    created.append(customer)

                except ValidationError as e:
                    errors.append(f"Record {index + 1}: {str(e)}")

        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProduct(graphene.Mutation):
    product = Field(ProductType)

    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int(required=False)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise ValidationError("Price must be positive")

        if stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock
        )

        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    order = Field(OrderType)

    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        if not product_ids:
            raise ValidationError("At least one product must be selected")

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")

        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise ValidationError("One or more product IDs are invalid")

        total_amount = sum(product.price for product in products)

        order = Order.objects.create(
            customer=customer,
            order_date=order_date or timezone.now(),
            total_amount=total_amount
        )

        order.products.set(products)

        return CreateOrder(order=order)

class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    products = List(ProductType)
    orders = List(OrderType)

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
