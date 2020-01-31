from django.core.exceptions import ValidationError

def validate_upi_id(value):
    if ('@' not in value) or (' ' in value):
        raise ValidationError(
                'Invalid UPI ID recieved. Check Again.'
            )