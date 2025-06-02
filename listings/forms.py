from django import forms
from .models import Listing, ListingImage, Feature

class ListingForm(forms.ModelForm):
    # Image files for multiple uploads
    image_files = forms.ImageField(
        required=False,
    )

    # Features field (Many-to-Many relationship)
    features = forms.ModelMultipleChoiceField(
        queryset=Feature.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Listing
        fields = [
            'title', 'price', 'location', 'size', 'description', 'features',
            'property_type', 'listing_type', 'availability', 'condition', 'furnishing'
        ]
