from math import ceil

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.views import View

from misago.conf import settings
from misago.readtracker.dates import get_cutoff_date
from misago.threads.permissions import exclude_invisible_posts
from misago.threads.viewmodels import ForumThread, PrivateThread


class GotoView(View):
    thread = None

    def get(self, request, pk, slug, **kwargs):
        thread = self.get_thread(request, pk, slug).unwrap()
        self.test_permissions(request, thread)

        posts_queryset = exclude_invisible_posts(
            request.user, thread.category, thread.post_set)

        target_post = self.get_target_post(
            request.user, thread, posts_queryset.order_by('id'), **kwargs)
        target_page = self.compute_post_page(target_post, posts_queryset)

        return self.get_redirect(thread, target_post, target_page)

    def get_thread(self, request, pk, slug):
        return self.thread(request, pk, slug)

    def test_permissions(self, request, thread):
        pass

    def get_target_post(self, user, thread, posts_queryset):
        raise NotImplementedError(
            "goto views should define their own get_target_post method")

    def compute_post_page(self, target_post, posts_queryset):
        # filter out events, order queryset
        posts_queryset = posts_queryset.filter(is_event=False).order_by('id')

        thread_length = posts_queryset.count()

        # is target an event?
        if target_post.is_event:
            target_event = target_post
            previous_posts = posts_queryset.filter(id__lt=target_event.id)
        else:
            previous_posts = posts_queryset.filter(id__lte=target_post.id)

        post_position = previous_posts.count()

        per_page = settings.MISAGO_POSTS_PER_PAGE - 1
        orphans = settings.MISAGO_POSTS_TAIL
        if orphans:
            orphans += 1

        hits = max(1, thread_length - orphans)
        thread_pages = int(ceil(hits / float(per_page)))

        if post_position >= thread_pages * per_page:
            return thread_pages

        return int(ceil(float(post_position) / (per_page)))

    def get_redirect(self, thread, target_post, target_page):
        thread_url = thread.thread_type.get_thread_absolute_url(
            thread, target_page)
        return redirect('%s#post-%s' % (thread_url, target_post.pk))


class ThreadGotoPostView(GotoView):
    thread = ForumThread

    def get(self, request, pk, slug, **kwargs):
        thread = self.get_thread(request, pk, slug).unwrap()
        self.test_permissions(request, thread)

        posts_queryset = exclude_invisible_posts(
            request.user, thread.category, thread.post_set)

        target_post = self.get_target_post(
            request, request.user, thread, posts_queryset.order_by('id'),
            **kwargs)
        if isinstance(target_post, HttpResponseRedirect):
            return target_post
        target_page = self.compute_post_page(target_post, posts_queryset)

        return self.get_redirect(thread, target_post, target_page)

    def get_target_post(self, request, user, thread, posts_queryset, **kwargs):
        try:
            return posts_queryset.get(pk=kwargs['post'])
        except ObjectDoesNotExist:
            messages.warning(request, _("This post is deleted."))
        return redirect(thread.get_last_post_url())
        # return get_object_or_404(posts_queryset, pk=kwargs['post'])


class ThreadGotoLastView(GotoView):
    thread = ForumThread

    def get_target_post(self, user, thread, posts_queryset, **kwargs):
        return posts_queryset.order_by('id').last()


class GetFirstUnreadPostMixin(object):
    def get_first_unread_post(self, user, posts_queryset):
        if user.is_authenticated:
            expired_posts = Q(posted_on__lt=get_cutoff_date(user))
            read_posts = Q(id__in=user.postread_set.values('post'))

            first_unread = posts_queryset.exclude(
                expired_posts | read_posts,
            ).order_by('id').first()

            if first_unread:
                return first_unread

        return posts_queryset.order_by('id').last()


class ThreadGotoNewView(GotoView, GetFirstUnreadPostMixin):
    thread = ForumThread

    def get_target_post(self, user, thread, posts_queryset, **kwargs):
        return self.get_first_unread_post(user, posts_queryset)


class ThreadGotoBestAnswerView(GotoView):
    thread = ForumThread

    def get_target_post(self, user, thread, posts_queryset, **kwargs):
        return thread.best_answer or thread.first_post


class ThreadGotoUnapprovedView(GotoView):
    thread = ForumThread

    def test_permissions(self, request, thread):
        if not thread.acl['can_approve']:
            raise PermissionDenied(
                _(
                    "You need permission to approve content to "
                    "be able to go to first unapproved post."
                )
            )

    def get_target_post(self, user, thread, posts_queryset, **kwargs):
        unapproved_post = posts_queryset.filter(
            is_unapproved=True,
        ).order_by('id').first()
        if unapproved_post:
            return unapproved_post
        else:
            return posts_queryset.order_by('id').last()


class PrivateThreadGotoPostView(GotoView):
    thread = PrivateThread

    def get_target_post(self, user, thread, posts_queryset, **kwargs):
        return get_object_or_404(posts_queryset, pk=kwargs['post'])


class PrivateThreadGotoLastView(GotoView):
    thread = PrivateThread

    def get_target_post(self, user, thread, posts_queryset, **kwargs):
        return posts_queryset.order_by('id').last()


class PrivateThreadGotoNewView(GotoView, GetFirstUnreadPostMixin):
    thread = PrivateThread

    def get_target_post(self, user, thread, posts_queryset, **kwargs):
        return self.get_first_unread_post(user, posts_queryset)
