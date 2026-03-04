# File: views.py
# Author: Declan Young (declanyg@bu.edu), 2/05/2026
# Description: views file to handle views for mini_insta app

from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile, Post, Photo
from django.db.models import Q

# Create your views here.
class ProfileLoginRequiredMixin(LoginRequiredMixin):
    login_url = "/login/"

    def get_profile(self):
        return Profile.objects.get(account=self.request.user)


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

class CreatePostView(ProfileLoginRequiredMixin, CreateView):
    model = Post
    fields = ['caption']
    template_name = "mini_insta/create_post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # profile = Profile.objects.get(pk=self.kwargs['pk'])
        # context['profile'] = profile
        context['profile'] = self.get_profile()

        return context

    def form_valid(self, form):
        post = form.save(commit=False)

        # post.profile = Profile.objects.get(pk=self.kwargs['pk'])
        post.profile = self.get_profile()

        post.save()

        # image_url = self.request.POST.get('image_url')
        # if image_url:
        #     Photo.objects.create(post=post, image_url=image_url)
        files = self.request.FILES.getlist('post-photos')
        for file in files:
            Photo.objects.create(post=post, image_file=file)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mini_insta:show_post')
    
    def get_object(self, queryset=None):
        return self.get_profile()

class UpdateProfileView(ProfileLoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['display_name', 'profile_image_url', 'bio_text']
    template_name = "mini_insta/update_profile_form.html"

    def get_success_url(self):
        return reverse('mini_insta:show_profile')
    
    def get_object(self, queryset=None):
        return self.get_profile()

class DeletePostView(ProfileLoginRequiredMixin, DeleteView):
    model = Post
    template_name = "mini_insta/delete_post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = Post.objects.get(pk=self.kwargs['pk'])
        context['post'] = post

        # profile = Post.objects.get(pk=self.kwargs['pk']).profile
        # context['profile'] = profile
        context["profile"] = self.get_profile()

        return context

    def get_success_url(self):
        return reverse('mini_insta:show_profile', kwargs={'pk': self.object.profile.pk})

class UpdatePostView(ProfileLoginRequiredMixin, UpdateView):
    model = Post
    fields = ['caption']
    template_name = "mini_insta/update_post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = Post.objects.get(pk=self.kwargs['pk'])
        context['post'] = post

        # profile = Post.objects.get(pk=self.kwargs['pk']).profile
        # context['profile'] = profile
        context["profile"] = self.get_profile()

        return context

    def get_success_url(self):
        return reverse('mini_insta:show_post', kwargs={'pk': self.object.pk})

class ShowFollowersDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_followers.html"
    context_object_name = "profile"

class ShowFollowingDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_following.html"
    context_object_name = "profile"

class PostFeedListView(ProfileLoginRequiredMixin, ListView):
    model = Post
    template_name = "mini_insta/show_feed.html"
    context_object_name = "posts"

    def get_queryset(self):
        # profile = Profile.objects.get(pk=self.kwargs["pk"])
        # return profile.get_post_feed()
        return self.get_profile().get_post_feed()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # context["profile"] = Profile.objects.get(pk=self.kwargs["pk"])
        context["profile"] = self.get_profile()

        return context
    
    def get_object(self, queryset=None):
        return self.get_profile()

class SearchView(ProfileLoginRequiredMixin,ListView):
    model = Profile
    template_name = "mini_insta/search_results.html"
    context_object_name = "profiles"

    def dispatch(self, request, *args, **kwargs):
        query = self.request.GET.get("q")
        if not query:
            self.template_name = "mini_insta/search.html"
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return Post.objects.filter(caption__icontains=query).order_by('-timestamp')

        return Profile.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # context["profile"] = Profile.objects.get(pk=self.kwargs["pk"])
        context["profile"] = self.get_profile()

        context["query"] = self.request.GET.get("q", "")

        context["posts"] = self.get_queryset()

        context["profiles"] = Profile.objects.filter(
            Q(username__icontains=context["query"]) |
            Q(display_name__icontains=context["query"]) |
            Q(bio_text__icontains=context["query"])
        ).order_by("username")

        return context

    def get_object(self, queryset=None):
        return self.get_profile()