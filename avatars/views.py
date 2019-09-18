from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from sorl.thumbnail.shortcuts import get_thumbnail
from .models import Avatar


def placeholder_response(size, email_hash):
    url = 'https://www.gravatar.com/avatar/{email_hash}?f=y&s={size}&d=mp'.format(
        size=size, email_hash=email_hash)
    return HttpResponseRedirect(url)


def avatar_view(request, email_hash=None, email=None, ext=None):
    try:
        size = int(request.GET.get('s', 80))
    except ValueError:
        return HttpResponse(status=400)

    default = request.GET.get('d', '').strip()
    if default:
        # Only 404 suported for now
        if default not in ('404',):
            return HttpResponse(status=400)

    if email_hash:
        try:
            avatar = Avatar.objects.get(email_hash=email_hash)
        except Avatar.DoesNotExist:
            if default == '404':
                return HttpResponse(status=404)
            return placeholder_response(size=size, email_hash=email_hash)
    else:
        email = email.strip().lower()
        try:
            avatar = Avatar.objects.get(email=email)
        except Avatar.DoesNotExist:
            avatar = Avatar(email=email)
            avatar.set_hash()

    if avatar.should_update():
        avatar.update_image()

    image = avatar.image
    if not image:
        return placeholder_response(size=size, email_hash=avatar.email_hash)

    image = get_thumbnail(image, '{size}x{size}'.format(size=size))

    response = HttpResponse(content_type='image/jpeg')
    response.write(image.storage.open(image.name, 'rb').read())
    return response
