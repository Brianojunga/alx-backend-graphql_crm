import graphene
from crm.schema import CRMQuery, BaseQuery, Mutation

class Query(CRMQuery, BaseQuery, graphene.ObjectType):
    pass

class Mutation(Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)