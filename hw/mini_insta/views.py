# File: views.py
# Author: Declan Young (declanyg@bu.edu), 2/05/2026
# Description: views file to handle views for mini_insta app
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile, Post, Photo, Follow, Like
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProfileSerializer, PostSerializer, PhotoSerializer, FollowSerializer, CommentSerializer, LikeSerializer

from contextvars import Token

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication

# Create your views here.
class ProfileLoginRequiredMixin(LoginRequiredMixin):
    login_url = "mini_insta:login"

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
        return reverse('mini_insta:show_post', kwargs={'pk': self.object.pk})
    
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

class PersonalProfileDetailView(ProfileLoginRequiredMixin, DetailView):
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return self.get_profile()

class CreateProfileView(CreateView):
    model = Profile
    fields = ['username', 'display_name', 'bio_text', 'profile_image_url']
    template_name = "mini_insta/create_profile_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user_registration_form"] = UserCreationForm()
        return context
    
    def form_valid(self, form):
        user_form = UserCreationForm(self.request.POST)
        if user_form.is_valid():
            user = user_form.save()

            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

            profile = form.save(commit=False)
            profile.account = user
            profile.save()
            
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('mini_insta:show_profile')

class FollowProfileView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follower = self.get_profile()
        target = Profile.objects.get(pk=self.kwargs['pk'])
        
        if follower != target:
            Follow.objects.get_or_create(follower_profile=follower, profile=target)
        
        return redirect(request.META.get('HTTP_REFERER'))
    
class DeleteFollowProfileView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follower = self.get_profile()
        target = Profile.objects.get(pk=self.kwargs['pk'])
        
        if follower != target:
            Follow.objects.filter(follower_profile=follower, profile=target).delete()
        
        return redirect(request.META.get('HTTP_REFERER'))

class LikePostView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        liker = self.get_profile()
        post = Post.objects.get(pk=self.kwargs['pk'])
        
        if liker != post.profile:
            Like.objects.get_or_create(profile=liker, post=post)
        
        return redirect(request.META.get('HTTP_REFERER'))

class DeleteLikePostView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        liker = self.get_profile()
        post = Post.objects.get(pk=self.kwargs['pk'])
        
        if liker != post.profile:
            Like.objects.filter(profile=liker, post=post).delete()
        
        return redirect(request.META.get('HTTP_REFERER'))


#Api Definitions

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_profiles(request):
    profiles = Profile.objects.all()
    serializer = ProfileSerializer(profiles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_profile_detail(request, pk):
    try:
        profile = Profile.objects.get(pk=pk)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ProfileSerializer(profile)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_profile_posts(request, pk):
    try:
        profile = Profile.objects.get(pk=pk)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    posts = Post.objects.filter(profile=profile).order_by('-timestamp')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_profile_pictures(request, pk):
    try:
        profile = Profile.objects.get(pk=pk)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    photos = Photo.objects.filter(post__profile=profile).order_by('-post__timestamp')
    serializer = PhotoSerializer(photos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_profile_feed(request, pk):
    try:
        profile = Profile.objects.get(pk=pk)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    posts = profile.get_post_feed()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_post_pictures(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    photos = Photo.objects.filter(post=post).order_by('-timestamp')
    serializer = PhotoSerializer(photos, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_create_post_for_profile(request, pk):
    try:
        profile = Profile.objects.get(pk=pk)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    caption = request.data.get("caption", "")
    image_url = request.data.get("image_url", None)

    if not caption:
        return Response(
            {"error": "caption is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    post = Post.objects.create(
        profile=profile,
        caption=caption
    )

    if image_url:
        Photo.objects.create(
            post=post,
            image_url=image_url
        )

    return Response(
        PostSerializer(post).data,
        status=status.HTTP_201_CREATED
    )

@api_view(["POST"])
def api_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token, _ = Token.objects.get_or_create(user=user)

    profile = Profile.objects.get(account=user)

    return Response({
        "token": token.key,
        "profile_id": profile.id,
        "profile_username": profile.username,
    })