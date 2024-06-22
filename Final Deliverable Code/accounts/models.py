from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Custom Manager for Account model
class MyAccountManager(BaseUserManager):
    # Function to create a normal user
    def create_user(self, first_name, last_name, username, email, address, password=None):
        if not email:
            raise ValueError('User must have an email address!')
        if not username:
            raise ValueError('User must have a username!')
        if not address:
            raise ValueError('User must have an address!')
        
        # Create a user model instance
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            address=address,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user
    
    # Function to create a superuser
    def create_superuser(self, first_name, last_name, address, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            address=address,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True

        user.save(using=self._db)
        return user


# Custom user model
class Account(AbstractBaseUser):
    # Fields for the custom user model
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True) 
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=13)
    address = models.CharField(max_length=100)

    # Additional fields for user model
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    # Permissions and status fields
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'address']

    objects = MyAccountManager()
    
    def __str__(self):
        return self.email
    
    # Check user permissions
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
