from django.shortcuts import render
from .models import Listing
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ListingForm
from .models import Listing, ListingImage, Feature
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import imagehash
from PIL import Image
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.conf import settings

import os


def aboutus(request):
    return render(request, 'aboutus.html')

@login_required
def aboutus2(request):
    return render(request, 'aboutus2.html')

def service(request):
    return render(request, 'service.html')

@login_required
def service2(request):
    return render(request, 'service2.html')

def home(request):
    #listings = Listing.objects.all()
    return render(request, 'home.html')
#, {'listings': listings}

@login_required
def home2(request):
    return render(request, 'home2.html')

@login_required
def add_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user  # Assign the logged-in user as the owner
            listing.save()

            # Handle multiple image uploads manually
            if 'image_files' in request.FILES:
                for image in request.FILES.getlist('image_files'):  # Get list of uploaded files
                    uploaded_image_hash = generate_image_hash(image)  # Generate image hash

                    # Check for duplicates
                    if check_image_similarity(uploaded_image_hash):
                        messages.error(request, "One of the uploaded images already exists!")
                        return redirect('add_listing')

                    # Save image to ListingImage model
                    listing_image = ListingImage(image=image, listing=listing, image_hash=uploaded_image_hash)
                    listing_image.save()

                # Link images to the listing
                listing.images.add(*ListingImage.objects.filter(listing=listing))

            selected_features = form.cleaned_data['features']  # Get selected features
            listing.features.set(selected_features)

            return redirect('home2')  # Redirect after saving
    else:
        form = ListingForm()

    return render(request, 'add_listing.html', {'form': form})



def listings(request):
    properties = Listing.objects.all().prefetch_related('images')
    all_features = Feature.objects.all()

    query = request.GET.get('q')
    location = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    size = request.GET.get('size')
    room_type = request.GET.get('room_type')
    featured = request.GET.get('featured')
    property_type = request.GET.get('property_type')
    listing_type = request.GET.get('listing_type')
    availability = request.GET.get('availability')
    features = request.GET.getlist('features')  # Multiple values allowed
    condition = request.GET.get('condition')
    furnishing = request.GET.get('furnishing')

    # Apply filters
    if query:
        properties = properties.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if location:
        properties = properties.filter(location__icontains=location)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if size:
        properties = properties.filter(size__icontains=size)
    if room_type:
        properties = properties.filter(size__icontains=room_type)  # Adjust as needed
    if featured == 'on':
        properties = properties.filter(featured=True)
    if property_type:
        properties = properties.filter(type__icontains=property_type)  # Make sure you have this field in your model
    if listing_type:
        properties = properties.filter(listing_type=listing_type)
    if availability:
        properties = properties.filter(availability=availability)
    if features:
        properties = properties.filter(features__id__in=features)
    if condition:
        properties = properties.filter(condition=condition)
    if furnishing:
        properties = properties.filter(furnishing=furnishing)

    sort_param = request.GET.get('sort', '')
    
    if sort_param == 'price_low':
        properties = properties.order_by('price')
    elif sort_param == 'price_high':
        properties = properties.order_by('-price')
    elif sort_param == 'newest':
        properties = properties.order_by('-updated_at')  # Change to your date field name
    elif sort_param == 'oldest':
        properties = properties.order_by('updated_at')   # Change to your date field name
    elif sort_param == 'title_az':
        properties = properties.order_by('title')
    elif sort_param == 'title_za':
        properties = properties.order_by('-title')
    else:
        # Default sorting (keep your original order or add default)
        properties = properties.order_by('-id')

    # Your existing pagination logic
    paginator = Paginator(properties, 10)  # Show 15 properties per page
    page = request.GET.get('page')

    try:
        properties_page = paginator.page(page)
    except PageNotAnInteger:
        properties_page = paginator.page(1)
    except EmptyPage:
        properties_page = paginator.page(paginator.num_pages)

    # Updated context to include sorting info
    context = {
        'properties': properties_page, 
        'all_features': all_features,
        'selected_features': features,  # Pass the selected features
        'current_sort': sort_param,     # Pass current sort for template
        'request': request,             # Make request available in template
    }

    return render(request, 'listings.html', context)

@login_required
def listings2(request):
    properties = Listing.objects.all().prefetch_related('images')
    all_features = Feature.objects.all()

    query = request.GET.get('q')
    location = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    size = request.GET.get('size')
    room_type = request.GET.get('room_type')
    featured = request.GET.get('featured')
    property_type = request.GET.get('property_type')
    listing_type = request.GET.get('listing_type')
    availability = request.GET.get('availability')
    features = request.GET.getlist('features')  # Multiple values allowed
    condition = request.GET.get('condition')
    furnishing = request.GET.get('furnishing')

    # Apply filters
    if query:
        properties = properties.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if location:
        properties = properties.filter(location__icontains=location)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if size:
        properties = properties.filter(size__icontains=size)
    if room_type:
        properties = properties.filter(size__icontains=room_type)  # Adjust as needed
    if featured == 'on':
        properties = properties.filter(featured=True)
    if property_type:
        properties = properties.filter(type__icontains=property_type)  # Make sure you have this field in your model
    if listing_type:
        properties = properties.filter(listing_type=listing_type)
    if availability:
        properties = properties.filter(availability=availability)
    if features:
        properties = properties.filter(features__id__in=features)
    if condition:
        properties = properties.filter(condition=condition)
    if furnishing:
        properties = properties.filter(furnishing=furnishing)

    sort_param = request.GET.get('sort', '')
    
    if sort_param == 'price_low':
        properties = properties.order_by('price')
    elif sort_param == 'price_high':
        properties = properties.order_by('-price')
    elif sort_param == 'newest':
        properties = properties.order_by('-updated_at')  # Change to your date field name
    elif sort_param == 'oldest':
        properties = properties.order_by('updated_at')   # Change to your date field name
    elif sort_param == 'title_az':
        properties = properties.order_by('title')
    elif sort_param == 'title_za':
        properties = properties.order_by('-title')
    else:
        # Default sorting (keep your original order or add default)
        properties = properties.order_by('-id')

    # Your existing pagination logic
    paginator = Paginator(properties, 10)  # Show 15 properties per page
    page = request.GET.get('page')

    try:
        properties_page = paginator.page(page)
    except PageNotAnInteger:
        properties_page = paginator.page(1)
    except EmptyPage:
        properties_page = paginator.page(paginator.num_pages)

    # Updated context to include sorting info
    context = {
        'properties': properties_page, 
        'all_features': all_features,
        'selected_features': features,  # Pass the selected features
        'current_sort': sort_param,     # Pass current sort for template
        'request': request,             # Make request available in template
    }


    return render(request, 'listings2.html', context)

def property_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    current_user_id = request.user.id if request.user.is_authenticated else None
    image_urls = [image.image.url for image in listing.images.all()]
    context = {
        'property': listing,
        'current_user_id': current_user_id,
        'image_urls': image_urls,
    }
    return render(request, 'property_detail.html', context)

def property_detail2(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    current_user_id = request.user.id if request.user.is_authenticated else None
    image_urls = [image.image.url for image in listing.images.all()]
    context = {
        'property': listing,
        'current_user_id': current_user_id,
        'image_urls': image_urls,
    }
    return render(request, 'property_detail2.html', context)

@login_required
def my_listings(request):
    user_properties = Listing.objects.filter(owner=request.user)
    return render(request, 'my_listings.html', {'properties': user_properties})

@login_required
def edit_property(request, id):
    property = get_object_or_404(Listing, id=id)

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()

            # Handle new image uploads (if any)
            if 'image_files' in request.FILES:
                for image in request.FILES.getlist('image_files'):  # Get a list of uploaded files
                    uploaded_image_hash = generate_image_hash(image)

                    # Check for duplicate images
                    if check_image_similarity(uploaded_image_hash):
                        messages.error(request, f"One of the uploaded images already exists in the system!")
                        return redirect('edit_property', id=listing.id)

                    listing_image = ListingImage(image=image, listing=listing, image_hash=uploaded_image_hash)
                    listing_image.save()
                    print(f"Image saved successfully: {listing_image.image.url}")
                listing.images.add(*ListingImage.objects.filter(listing=listing))

            # Handle image deletions (if any)
            if 'delete_images' in request.POST:
                delete_image_ids = request.POST.getlist('delete_images')  # Get selected image IDs to delete
                for image_id in delete_image_ids:
                    image = ListingImage.objects.get(id=image_id)  # Get the image instance
                    image.delete()  # Delete the image

            return redirect('my_listings')  # Redirect to the listings page after saving
    else:
        form = ListingForm(instance=property)

    return render(request, 'edit_property.html', {'form': form, 'property': property})



def generate_image_hash(uploaded_image):
    """Generate a perceptual hash for the uploaded image."""
    image = Image.open(uploaded_image)
    return str(imagehash.average_hash(image))  # Generate hash using average hash (can use dhash, etc.)

def check_image_similarity(uploaded_image_hash):
    """Check if an uploaded image's hash matches any existing image hash in the database."""
    existing_images = ListingImage.objects.all()  # Get all images from the database
    for image in existing_images:
        if image.image_hash == uploaded_image_hash:  # Compare the hashes
            return True  # Match found, return True
    return False  # No match found, return False


@login_required
def delete_property(request, id):
    property = get_object_or_404(Listing, id=id)

    if request.method == 'POST':
        property.delete()
        return redirect('my_listings')

    return render(request, 'delete_property.html', {'property': property})

def check_files(request):
    """Check what files are actually in the media directories"""
    try:
        output = []
        output.append("=== FILES IN MEDIA DIRECTORIES ===")
        
        directories_to_check = [
            '/mnt/storage/images',
            '/mnt/storage/images/property_images',
            '/app/media',
            '/app/media/property_images'
        ]
        
        for directory in directories_to_check:
            output.append(f"\n--- {directory} ---")
            try:
                if os.path.exists(directory):
                    files = os.listdir(directory)
                    if files:
                        output.append(f"Files found: {len(files)}")
                        # Show first 5 files
                        for file in files[:5]:
                            file_path = os.path.join(directory, file)
                            size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                            output.append(f"  - {file} ({size} bytes)")
                        if len(files) > 5:
                            output.append(f"  ... and {len(files) - 5} more files")
                    else:
                        output.append("Directory is empty")
                else:
                    output.append("Directory does not exist")
            except Exception as e:
                output.append(f"Error accessing directory: {str(e)}")
        
        # Check database for image references
        output.append("\n=== DATABASE IMAGE REFERENCES ===")
        try:
            from .models import Property
            properties = Property.objects.exclude(image='').exclude(image__isnull=True)[:3]
            output.append(f"Properties with images in DB: {properties.count()}")
            
            for prop in properties:
                output.append(f"Property {prop.id}:")
                output.append(f"  Image field: {prop.image}")
                output.append(f"  Image URL: {prop.image.url}")
                output.append(f"  Image path: {prop.image.path}")
                output.append(f"  File exists: {os.path.exists(prop.image.path)}")
        except Exception as e:
            output.append(f"Error checking database: {str(e)}")
        
        return HttpResponse('\n'.join(output), content_type='text/plain')
    
    except Exception as e:
        return HttpResponse(f"ERROR: {str(e)}", content_type='text/plain')
    
def simple_debug(request):
    """Ultra simple debug view"""
    try:
        from django.conf import settings
        
        output = []
        output.append("=== DJANGO MEDIA DEBUG ===")
        output.append(f"MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'NOT SET')}")
        output.append(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'NOT SET')}")
        output.append(f"DEBUG: {getattr(settings, 'DEBUG', 'NOT SET')}")
        output.append("")
        
        output.append("=== ENVIRONMENT ===")
        output.append(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'NOT SET')}")
        output.append(f"DATABASE_URL exists: {'DATABASE_URL' in os.environ}")
        output.append("")
        
        output.append("=== DIRECTORIES ===")
        for path in ['/app', '/app/media', '/mnt/storage', '/mnt/storage/images']:
            exists = os.path.exists(path)
            output.append(f"{path}: {'EXISTS' if exists else 'NOT FOUND'}")
        
        return HttpResponse('\n'.join(output), content_type='text/plain')
    
    except Exception as e:
        return HttpResponse(f"ERROR: {str(e)}", content_type='text/plain')