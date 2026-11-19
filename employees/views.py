from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import BootstrapAuthenticationForm


def landing(request):
    return render(request, 'landing.html')


class HRLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = BootstrapAuthenticationForm
    redirect_authenticated_user = True


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard(request):
    # Placeholder: the full dashboard is built in Task 5.
    return render(request, 'dashboard.html')