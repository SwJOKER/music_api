from rest_framework import status
from rest_framework.response import Response


class AutoManySerializerMixin:
    """ Provides feature which allow sending list of objects. Switchs serializer to 'many' """
    def create(self, request, *args, **kwargs):
        many = True if isinstance(request.data, list) else False
        serializer = self.get_serializer(data=request.data, many=many)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DiscreteRetrieveSerializerMixin:
    """ Define discrete serializer for retrieve action. Child must contain attribute:
        - retrieve_serializer_class
     """
    retrieve_serializer_class = None

    def get_serializer_class(self):
        if self.retrieve_serializer_class is None:
            raise NotImplementedError(f'{self.__class__.__name__}: not defined "retrieve_serializer_class"')
        if self.action == 'retrieve':
            return self.retrieve_serializer_class
        return super().get_serializer_class()
