from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.views.generic import DetailView, CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .models import Post, UserProfile, User
from django.db.models import Q
from .forms import CommentForm, PostForm, EditUserProfileForm, ChangePasswordForm, CreateProfileForm


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by('created_date')
    template_name = 'index.html'
    paginate_by = 10


class PostDetail(View):

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by('created_date')
        upvoted = False
        if post.upvotes.filter(id=self.request.user.id).exists():
            upvoted = True
        downvoted = False
        if post.downvotes.filter(id=self.request.user.id).exists():
            downvoted = True

        return render(
            request,
            'post_detail.html', {
                "post": post,
                "comments": comments,
                "commented": False,
                "upvoted": upvoted,
                "downvoted": downvoted,
                "comment_form": CommentForm()
            },)

    def post(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by('created_date')
        upvoted = False
        if post.upvotes.filter(id=self.request.user.id).exists():
            upvoted = True
        downvoted = False
        if post.downvotes.filter(id=self.request.user.id).exists():
            downvoted = True

        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
            request,
            'post_detail.html', {
                "post": post,
                "comments": comments,
                "commented": True,
                "commented": False,
                "upvoted": upvoted,
                "downvoted": downvoted,
                "comment_form": CommentForm()
            },)


class PostUpVotes(View):

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)

        if post.upvotes.filter(id=request.user.id).exists():
            post.upvotes.remove(request.user)
        else:
            post.upvotes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class PostDownVotes(View):

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)

        if post.downvotes.filter(id=request.user.id).exists():
            post.downvotes.remove(request.user)
        else:
            post.downvotes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class PostCreate(View):
    model = Post

    def get(self, request):
        post_form = PostForm()
        context = {"post_form": post_form}
        return render(request, 'post_create.html', context)

    def post(self, request, *args, **kwargs):

        post_form = PostForm(request.POST)

        if post_form.is_valid():

            post_form.instance.author = request.user
            # post_form.instance.status = 0
            post = post_form.save(commit=False)
            # post.post = post
            post.save()
            return HttpResponseRedirect('post_detail/')

        context = {'post_form': post_form}
        return render(request, 'post_create.html', context)


def PostSearch(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        posts = Post.objects.filter(Q(content__icontains=searched) | Q(title__icontains=searched))
        return render(
            request,
            'post_search.html',
            {'searched': searched, 'posts': posts})
    else:
        return render(request, 'post_search.html')


class UserEdit(generic.UpdateView):
    form_class = EditUserProfileForm
    template_name = 'edit_user.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user


class ChangePassword(PasswordChangeView):
    form_class = ChangePasswordForm
    template_name = 'change_password.html'
    success_url = reverse_lazy('home')


def password_success(request):
    return render(request, 'password_success.html', {})


class UserProfilePage(DetailView):
    model = UserProfile
    template_name = 'view_profile.html'

    def get_context_data(self, *args, **kwargs):

        selected_user = get_object_or_404(UserProfile, id=self.kwargs['pk'])

        user_posts = Post.objects.filter(author=selected_user.user)

        context = super().get_context_data(*args, **kwargs)

        context["selected_user"] = selected_user
        context["user_posts"] = user_posts
        return context


class EditProfilePage(generic.UpdateView):

    model = UserProfile
    template_name = 'edit_profile.html'
    fields = ['bio', 'profile_picture', 'website_url', 'facebook_url', 'instagram_url', 'twitter_url']
    success_url = reverse_lazy('home')


class CreateProfilePage(CreateView):
    model = UserProfile
    form_class = CreateProfileForm
    template_name = 'create_profile_page.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
