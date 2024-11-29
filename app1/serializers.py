from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Product
from django.contrib.auth import authenticate

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password']

    def validate_password(self, value):
        """
        Ensure the password meets the required validation rules.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value    

    def create(self, validated_data):
        """
        Create a new user with validated data and return the user object.
        """
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate user using email instead of username
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'price', 'discount', 'user']

    # Ensure product_name is required and not empty
    product_name = serializers.CharField(required=True, allow_blank=False)

    # Ensure price is required and positive
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)

    # Ensure discount is required but non-negative
    discount = serializers.DecimalField(required=True, max_digits=5, decimal_places=2)

    def validate_product_name(self, value):
        """
        Ensure that the product name is not empty and is required.
        """
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Product name cannot be empty.")
        return value

    def validate_price(self, value):
        """
        Ensure that the price is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_discount(self, value):
        """
        Ensure that the discount is non-negative and less than the price.
        """
        if value < 0:
            raise serializers.ValidationError("Discount cannot be negative.")
        return value

    def validate(self, data):
        """
        Custom validation to ensure the discount is not greater than the price.
        """
        if data['discount'] > data['price']:
            raise serializers.ValidationError("Discount cannot be greater than the price.")
        return data

    def create(self, validated_data):
        """
        Create a new product and assign the user automatically.
        """
        user = self.context['request'].user
        product = Product.objects.create(user=user, **validated_data)
        return product
