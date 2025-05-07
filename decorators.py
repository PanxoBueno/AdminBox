from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def atleta_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.tipo_usuario != 'atleta':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def entrenador_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.tipo_usuario != 'entrenador':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def tipo_usuario_required(*tipos_permitidos):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.tipo_usuario not in tipos_permitidos and not request.user.is_superuser:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator