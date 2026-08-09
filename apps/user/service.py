
from apps.user.models import User

def create_user(user_data):
    
    if not user_data.get('email') or not user_data.get('password'):
        raise ValueError("Email and password are required to create a user.")
    
    # Create a new User instance
    user = User.objects.create(**user_data)
    return user


