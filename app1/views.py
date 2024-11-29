from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import CustomUserSerializer, LoginSerializer, ProductSerializer
from .models import Product
from rest_framework.permissions import AllowAny

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]  # No changes needed, allows unauthenticated access

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]  # No changes needed, allows unauthenticated access

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DashboardAPIView(APIView):
    permission_classes = [AllowAny]  # Change to IsAuthenticated

    def get(self, request):
        user = request.user
        return Response({
            "message": f"Welcome, {user.first_name}!",
            "user_info": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        })

class ProductCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Passing request context so that ProductSerializer can access the user
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductRetrieveAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        user = request.user
        try:
            product = Product.objects.get(pk=pk, user=request.user)
        except Product.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data)

class ProductUpdateAPIView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, pk):
        user = request.user
        try:
            product = Product.objects.get(pk=pk, user=request.user)
        except Product.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, user=request.user)
        except Product.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response({"detail": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
