import graphene
from crm.schema import CRMQuery, Query, Mutation

class MainQuery(CRMQuery, Query, graphene.ObjectType):
    pass

class Mutation(Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=MainQuery, mutation=Mutation)