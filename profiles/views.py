from django.contrib.auth.models import User
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import auth, messages
from django.views.generic import FormView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from profiles.forms import UserLoginForm, UserRegistrationForm, UserModelForm
from profiles.forms import ProfileModelForm, ProfilePasswordRecoveryForm
from profiles.forms import ProfileSetPasswordForm
from profiles.models import Profile


class LoginFormView(FormView):
    template_name = 'profiles/login.html'
    success_url = reverse_lazy('drevo')
    form_class = UserLoginForm

    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('profiles:myprofile'))
        return super().get(request, *args, **kwargs)


class RegistrationFormView(CreateView):
    template_name = 'profiles/register.html'
    success_url = reverse_lazy('profiles:login')
    form_class = UserRegistrationForm
    model = User

    def form_valid(self, form):
        if form.is_valid():
            user = form.save()

            user.profile.deactivate_user()
            user.profile.generate_activation_key()
            user.profile.send_verify_mail()

            messages.success(
                self.request,
                'Вы успешно зарегистрировались! '
                'Для подтверждения учетной записи перейдите по ссылке, '
                'отправленной на адрес электронной почты, '
                'указанный Вами при регистрации.'
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('drevo'))
        return super().get(request, *args, **kwargs)


class LogoutFormView(LoginRequiredMixin, FormView):
    def get(self, request, *args, **kwargs):
        auth.logout(self.request)
        return HttpResponseRedirect(reverse('drevo'))


class ProfileFormView(LoginRequiredMixin, UpdateView):
    template_name = 'profiles/myprofile.html'
    success_url = reverse_lazy('profiles:myprofile')
    form_class = UserModelForm
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш профиль'
        context['profile_form'] = ProfileModelForm(
            instance=Profile.objects.get(user=self.object)
        )
        return context

    def get_object(self, queryset=None):
        self.kwargs[self.pk_url_kwarg] = self.request.user.id
        return super().get_object()

    def form_valid(self, form):
        profile_form = self.get_form(ProfileModelForm)
        profile_form.instance = Profile.objects.get(user=self.object)

        if profile_form.is_valid():
            image = self.request.FILES.get('image')
            if image:
                image.name = f'{self.request.user.username}.{image.name.split(".")[-1]}'
                profile_form.instance.avatar = image

            profile_form.save()
            return super().form_valid(form)

        return HttpResponseRedirect(reverse('profiles:myprofile'))


class ProfileTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/usersprofile.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['object'] = None

        _id = self.kwargs.get(self.pk_url_kwarg)
        if _id:
            _object = get_object_or_404(User, id=_id)

            if _object:
                context['object'] = _object

        context['title'] = f'Профиль пользователя {_object.username}'
        return context


class ProfileVerifyView(TemplateView):
    template_name = 'profiles/verification.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.context_data['user'] = None

        username = kwargs.get('username')
        activation_key = kwargs.get('activation_key')

        if username and activation_key:
            user = User.objects.get(username=username)

            if user:
                if user.profile.verify(username, activation_key):
                    auth.login(request, user)
                    response.context_data['user'] = user

        return response


class ProfilePasswordRecoveryFormView(FormView):
    template_name = 'profiles/password_recovery.html'
    success_url = reverse_lazy('profiles:login')
    form_class = ProfilePasswordRecoveryForm

    def form_valid(self, form):
        if form.is_valid():
            email = form.cleaned_data.get('email')
            profile = Profile.objects.get(user__email=email)

            if profile:
                profile.generate_password_recovery_key()
                profile.send_password_recovery_mail()
                messages.success(
                    self.request,
                    'Письмо со ссылкой для восстановления пароля '
                    'отправлено на указанный адрес эл. почты.')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановление пароля'
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('profiles:myprofile'))
        return super().get(request, *args, **kwargs)


class ProfileSetPasswordFormView(FormView):
    template_name = 'profiles/password_recovery_update.html'
    success_url = reverse_lazy('profiles:login')
    form_class = ProfileSetPasswordForm

    def form_valid(self, form):
        if form.is_valid():
            email = self.kwargs.get('email')
            key = self.kwargs.get('password_recovery_key')

            if email and key:
                profile = Profile.objects.get(user__email=email)

                if profile.recovery_valid(email, key):
                    form.save()

                    profile.password_recovery_key = ''
                    profile.password_recovery_key_expires = None
                    profile.save()

                    messages.success(self.request, 'Ваш пароль успешно изменён.')
                    return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановление пароля'
        context['full_url'] = self.request.get_full_path()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        email = self.kwargs.get('email')

        user = User.objects.get(email=email)
        kwargs['user'] = user

        return kwargs

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        email = self.kwargs.get('email')
        key = self.kwargs.get('password_recovery_key')

        if not email or not key:
            raise Http404

        user = get_object_or_404(User, email=email)
        self.kwargs['user'] = user

        if not user.profile.recovery_valid(email, key):
            raise Http404

        return super().get(request, *args, **kwargs)