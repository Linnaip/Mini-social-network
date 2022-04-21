from django.utils import timezone, dateformat


def year(request):
    """Добавляет переменную с текущим годом."""
    year = dateformat.format(timezone.now(), 'Y')
    return {
        'year': year
    }
