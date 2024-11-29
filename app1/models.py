from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError  # Corrected import

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        # Create the user instance without setting the password initially
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        
        if password:
            # Validate the password before setting it
            try:
                validate_password(password, user)
            except ValidationError as e:
                raise ValueError(f"Password validation failed: {', '.join(e.messages)}")

            # Set the password after validation
            user.set_password(password)
        else:
            raise ValueError('Password must be provided')
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        # Set is_staff and is_superuser before saving, it's good practice to do this before saving
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # date_joined = models.DateTimeField(auto_now_add=True)  # Track when the user joined
    last_login = models.DateTimeField(auto_now=True) 

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def get_full_name(self):
        # Return full name by combining first and last names
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        # Return short name (first name)
        return self.first_name

    def save(self, *args, **kwargs):
        # Optionally, add custom save logic (e.g., lowercase email)
        self.email = self.email.lower()  # Ensure email is always stored in lowercase
        super().save(*args, **kwargs)

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.product_name
    
    def clean(self):
        """
        Custom validation to ensure discount is not greater than price.
        """
        if self.discount > self.price:
            raise ValidationError("Discount cannot be greater than the price.")

    def get_final_price(self):
        """
        Returns the final price after applying the discount.
        """
        return self.price - self.discount

    class Meta:
        ordering = ['product_name']
