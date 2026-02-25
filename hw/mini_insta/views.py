# File: views.py
# Author: Declan Young (declanyg@bu.edu), 2/05/2026
# Description: views file to handle views for mini_insta app

from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Profile, Post, Photo

# Create your views here.
class ProfileListView(ListView):
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"

class ProfileDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

class PostDetailView(DetailView):
    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = "post"

class CreatePostView(CreateView):
    model = Post
    fields = ['caption']
    template_name = "mini_insta/create_post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile = Profile.objects.get(pk=self.kwargs['pk'])
        context['profile'] = profile

        return context

    def form_valid(self, form):
        post = form.save(commit=False)

        post.profile = Profile.objects.get(pk=self.kwargs['pk'])

        post.save()

        # image_url = self.request.POST.get('image_url')
        # if image_url:
        #     Photo.objects.create(post=post, image_url=image_url)
        files = self.request.FILES.getlist('post-photos')
        for file in files:
            Photo.objects.create(post=post, image_file=file)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mini_insta:show_post', kwargs={'pk': self.object.pk})

class UpdateProfileView(UpdateView):
    model = Profile
    fields = ['display_name', 'profile_image_url', 'bio_text']
    template_name = "mini_insta/update_profile_form.html"

    def get_success_url(self):
        return reverse('mini_insta:show_profile', kwargs={'pk': self.object.pk})