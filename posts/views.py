from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.views import generic

from . import forms
from . import models

from django.contrib.auth import get_user_model
User = get_user_model()


class PostList(generic.ListView):
    model = models.Post

    def get_queryset(self):
        return models.Post.objects.select_related("user", "group")


class UserPosts(generic.ListView):
    model = models.Post
    template_name = "posts/user_post_list.html"

    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related("posts").get(
                username__iexact=self.kwargs.get("username")
            )
        except User.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_user"] = self.post_user
        return context


class PostDetail(generic.DetailView):
    model = models.Post

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related("user", "group").filter(
            user__username__iexact=self.kwargs.get("username")
        )


class CreatePost(LoginRequiredMixin, generic.CreateView):
    # form_class = forms.PostForm
    fields = ('message','group')
    model = models.Post

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update({"user": self.request.user})
    #     return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class DeletePost(LoginRequiredMixin, generic.DeleteView):
    model = models.Post
    success_url = reverse_lazy("posts:all")

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related("user", "group").filter(user_id=self.request.user.id)

    def delete(self, *args, **kwargs):
        messages.success(self.request, "Post Deleted")
        return super().delete(*args, **kwargs)
