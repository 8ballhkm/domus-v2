import uuid
from django.db import models
import imagehash
from django.conf import settings
from PIL import Image


class Listing(models.Model):
    PROPERTY_TYPES = [
        ('House', 'House'),
        ('Apartment', 'Apartment'),
        ('Commercial', 'Commercial'),
        ('Land', 'Land'),
        ('Condo', 'Condo'),
        ('Penthouse', 'Penthouse'),
    ]
    LISTING_TYPES = [
        ('For Sale', 'For Sale'),
        ('For Rent', 'For Rent'),
        ('Auction', 'Auction'),
    ]
    
    AVAILABILITY = [
        ('Immediate', 'Immediate'),
        ('Coming Soon', 'Coming Soon'),
    ]
    
    PROPERTY_FEATURES = [
        ('Pool', 'Swimming Pool'),
        ('Gym', 'Gym'),
        ('Parking', 'Parking'),
        ('Balcony', 'Balcony'),
        ('Garden', 'Garden'),
        ('Air Conditioned', 'Air Conditioned'),
    ]
    
    CONDITION_CHOICES = [
        ('New', 'New'),
        ('Renovated', 'Renovated'),
        ('Pre-owned', 'Pre-owned'),
    ]
    
    FURNISHING_CHOICES = [
        ('Unfurnished', 'Unfurnished'),
        ('Partially Furnished', 'Partially Furnished'),
        ('Fully Furnished', 'Fully Furnished'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='listings',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    STATES = [
        ('Johor', 'Johor'),
        ('Kedah', 'Kedah'),
        ('Kelantan', 'Kelantan'),
        ('Melaka', 'Melaka'),
        ('Negeri Sembilan', 'Negeri Sembilan'),
        ('Pahang', 'Pahang'),
        ('Perak', 'Perak'),
        ('Perlis', 'Perlis'),
        ('Penang', 'Penang'),
        ('Sabah', 'Sabah'),
        ('Sarawak', 'Sarawak'),
        ('Selangor', 'Selangor'),
        ('Terengganu', 'Terengganu'),
        ('Kuala Lumpur', 'Kuala Lumpur'),
        ('Putrajaya', 'Putrajaya'),
        ('Labuan', 'Labuan')
    ]
    location = models.CharField(
        max_length=50,
        choices=STATES,
        default=''
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES, default='')
    room_count = models.IntegerField(default=1)
    ROOM = [
        ('-', '-'),
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large'),
        ('Master', 'Master')
    ]
    size = models.CharField(
        max_length=50,
        choices=ROOM,
        default=''
    )
    description = models.TextField()
    images = models.ManyToManyField('ListingImage', related_name='listings', blank=True)
    listing_type = models.CharField(max_length=50, choices=LISTING_TYPES, default='')
    availability = models.CharField(max_length=50, choices=AVAILABILITY, default='')
    features = models.ManyToManyField('Feature', blank=True)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, default='')
    furnishing = models.CharField(max_length=50, choices=FURNISHING_CHOICES, default='')

    def __str__(self):
        return self.title

class Feature(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ListingImage(models.Model):
    image = models.ImageField(upload_to='property_images/', default='property_images/default.jpg')
    listing = models.ForeignKey(Listing, related_name='listing_images', on_delete=models.CASCADE)
    image_hash = models.CharField(max_length=32, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.image and not self.image_hash:
            self.image_hash = self.get_image_hash()  # Generate and assign the hash
        super().save(*args, **kwargs)

    def get_image_hash(self):
        try:
            # Get the image path for local storage or URL for GCS
            image_url = self.image.url
            image = Image.open(image_url)  # Open image from URL in GCS
            hash = imagehash.average_hash(image)  # Generate hash
            return str(hash)
        except Exception as e:
            print(f"Error: {e}")
            return None

    def __str__(self):
        return f"Image for {self.listing.title}"