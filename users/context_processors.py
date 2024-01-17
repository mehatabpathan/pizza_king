from django.contrib.auth.models import Group


def worker_status(request):
    is_worker = request.user.groups.filter(name='Worker').exists()
    return {'is_worker': is_worker}