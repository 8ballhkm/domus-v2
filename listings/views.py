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

            # Handle multiple image uploads manually (get all files from request.FILES)
            if 'image_files' in request.FILES:
                for image in request.FILES.getlist('image_files'):  # Get a list of uploaded files
                    uploaded_image_hash = generate_image_hash(image)  # Generate the hash for the uploaded image

                    # Check for duplicates before saving
                    if check_image_similarity(uploaded_image_hash):
                        messages.error(request, "One of the uploaded images already exists in the system!")
                        return redirect('add_listing')  # Redirect back to add listing page

                    # Save the new image if no duplicate is found
                    listing_image = ListingImage(image=image, listing=listing, image_hash=uploaded_image_hash)
                    listing_image.save()  # Save only after checking for duplicates

                listing.images.add(*ListingImage.objects.filter(listing=listing))  # Link the images to the listing
            
            selected_features = form.cleaned_data['features']  # Get selected features
            listing.features.set(selected_features)

            return redirect('home2')  # Redirect to your desired page after saving
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

    # Pagination
    paginator = Paginator(properties, 15)  # Show 15 properties per page
    page = request.GET.get('page')

    try:
        properties_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        properties_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        properties_page = paginator.page(paginator.num_pages)

    return render(request, 'listings.html', {'properties': properties_page, 'all_features': all_features})

@login_required
def listings2(request):
    properties = Listing.objects.all().prefetch_related('images')
    all_features = Feature.objects.all()
    # Get the query parameters from the URL
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
        properties = properties.filter(features__name__in=features)
    if condition:
        properties = properties.filter(condition=condition)
    if furnishing:
        properties = properties.filter(furnishing=furnishing)

    features = request.GET.getlist('features')
    print("Selected features:", features)

    if features:
        properties = properties.filter(features__name__in=features)


    return render(request, 'listings2.html', {'properties': properties, 'all_features': all_features})

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