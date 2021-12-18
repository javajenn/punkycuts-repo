from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.utils.timezone import now
from django.utils.translation import gettext as _, gettext_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView, TemplateView, View
from django.core.files.storage import FileSystemStorage

from store_index.models import Customer

from .fields import autocompleter_app
from .forms import WriteForm, AnonymousWriteForm, QuickReplyForm, FullReplyForm
from .models import OPTION_MESSAGES, Message, get_order_by
from .utils import format_subject, format_body

login_required_m = method_decorator(login_required)
csrf_protect_m = method_decorator(csrf_protect)
never_cache_m = method_decorator(never_cache)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters('subject', 'body'))


##########
# Helpers
##########
def _get_referer(request):
    """Return the HTTP_REFERER, if existing."""
    if 'HTTP_REFERER' in request.META:
        sr = urlsplit(request.META['HTTP_REFERER'])
        return urlunsplit(('', '', sr.path, sr.query, sr.fragment))


def _get_safe_internal_url(urlstring):
    """Return the URL without the scheme part and the domain part, if present."""
    if urlstring:
        sr = urlsplit(urlstring)
        return urlunsplit(('', '', sr.path, sr.query, sr.fragment))


########
# Views
########
class IndexView(RedirectView):
    """
    Redirect to the inbox folder view, taking care to stay sticked to the targeted application instance
    when there is more than one instance.

    """
    pattern_name = 'postman:inbox'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        return reverse(self.pattern_name,
            args=args, kwargs=kwargs,
            current_app=self.request.resolver_match.namespace)


class NamespaceMixin(object):
    """Common code to manage the namespace."""

    def render_to_response(self, context, **response_kwargs):
        self.request.current_app = self.request.resolver_match.namespace
        return super().render_to_response(context, **response_kwargs)


class FolderMixin(NamespaceMixin, object):
    """Code common to the folders."""
    http_method_names = ['get']

    @never_cache_m
    @login_required_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = {'query_dict': self.request.GET}
        option = kwargs.get('option')
        if option:
            params['option'] = option
        order_by = get_order_by(self.request.GET)
        if order_by:
            params['order_by'] = order_by
        msgs = getattr(Message.objects, self.folder_name)(self.request.user, **params)
        viewname = 'postman:' + self.view_name
        current_instance = self.request.resolver_match.namespace
        context.update({
            'pm_messages': msgs,  # avoid 'messages', already used by contrib.messages
            'by_conversation': option is None,
            'by_message': option == OPTION_MESSAGES,
            'by_conversation_url': reverse(viewname, current_app=current_instance),
            'by_message_url': reverse(viewname, args=[OPTION_MESSAGES], current_app=current_instance),
            'current_url': self.request.get_full_path(),
            'gets': self.request.GET,  # useful to postman_order_by template tag
        })
        return context

@login_required
class InboxView(FolderMixin, TemplateView):
    """
    Display the list of received messages for the current user.

    Optional URLconf name-based argument:
        ``option``: display option:
            OPTION_MESSAGES to view all messages
            default to None to view only the last message for each conversation
    Optional URLconf configuration attribute:
        ``template_name``: the name of the template to use

    """
    # for FolderMixin:
    folder_name = 'inbox'
    view_name = 'inbox'
    # for TemplateView:
    template_name = 'postman/inbox.html'
    # def get(self, request):
    #     userid = request.user.pk
    #     try:
    #         customer = Customer.objects.get(User_id=userid)
    #     except Customer.DoesNotExist:
    #         customer = None
    #     if not customer.is_email_verified:
    #         messages.add_message(request, messages.ERROR, 'Email is not verified. Please check inbox and spam folder.')
    #         return redirect('index')
    #     else:
    #         context = super().get_context_data()
    #         return render(request, self.template_name, context)


class SentView(FolderMixin, TemplateView):
    """
    Display the list of sent messages for the current user.

    Optional arguments and attributes: refer to InboxView.

    """
    # for FolderMixin:
    folder_name = 'sent'
    view_name = 'sent'
    # for TemplateView:
    template_name = 'postman/sent.html'


class ArchivesView(FolderMixin, TemplateView):
    """
    Display the list of archived messages for the current user.

    Optional arguments and attributes: refer to InboxView.

    """
    # for FolderMixin:
    folder_name = 'archives'
    view_name = 'archives'
    # for TemplateView:
    template_name = 'postman/archives.html'


class TrashView(FolderMixin, TemplateView):
    """
    Display the list of deleted messages for the current user.

    Optional arguments and attributes: refer to InboxView.

    """
    # for FolderMixin:
    folder_name = 'trash'
    view_name = 'trash'
    # for TemplateView:
    template_name = 'postman/trash.html'


class ComposeMixin(NamespaceMixin, object):
    """
    Code common to the write and reply views.

    Optional attributes:
        ``success_url``: where to redirect to after a successful POST
        ``user_filter``: a filter for recipients
        ``exchange_filter``: a filter for exchanges between a sender and a recipient
        ``max``: an upper limit for the recipients number
        ``auto_moderators``: a list of auto-moderation functions

    """
    http_method_names = ['get', 'post']
    success_url = None
    user_filter = None
    exchange_filter = None
    max = None
    auto_moderators = []

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            kwargs.update({
                'sender': self.request.user,
                'user_filter': self.user_filter,
                'exchange_filter': self.exchange_filter,
                'max': self.max,
                'site': get_current_site(self.request),
            })
        return kwargs

    def get_success_url(self):
        return _get_safe_internal_url(self.request.GET.get('next')) or self.success_url or _get_referer(self.request) or 'postman:inbox'

    def form_valid(self, form):
        params = {'auto_moderators': self.auto_moderators}
        if hasattr(self, 'parent'):  # only in the ReplyView case
            params['parent'] = self.parent
        is_successful = form.save(**params)
        if is_successful:
            messages.success(self.request, _("Message successfully sent."), fail_silently=True)
        else:
            messages.warning(self.request, _("Message rejected for at least one recipient."), fail_silently=True)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'autocompleter_app': autocompleter_app,
            'next_url': self.request.GET.get('next') or _get_referer(self.request),
        })
        return context


class WriteView(ComposeMixin, FormView):
    """
    Display a form to compose a message.

    Optional URLconf name-based argument:
        ``recipients``: a colon-separated list of usernames
    Optional attributes:
        ``form_classes``: a 2-tuple of form classes
        ``autocomplete_channels``: a channel name or a 2-tuple of names
        ``template_name``: the name of the template to use
        + those of ComposeMixin

    """
    form_classes = (WriteForm, AnonymousWriteForm)
    autocomplete_channels = None
    template_name = 'postman/write.html'

    @sensitive_post_parameters_m
    @never_cache_m
    @csrf_protect_m
    def dispatch(self, *args, **kwargs):
        if getattr(settings, 'POSTMAN_DISALLOW_ANONYMOUS', False):
            return login_required(super().dispatch)(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def get_form_class(self):
        return self.form_classes[0 if self.request.user.is_authenticated else 1]

    def get_initial(self):
        initial = super().get_initial()
        if self.request.method == 'GET':
            initial.update(self.request.GET.items())  # allow optional initializations by query string
            recipients = self.kwargs.get('recipients')
            if recipients:
                # order_by() is not mandatory, but: a) it doesn't hurt; b) it eases the test suite
                # and anyway the original ordering cannot be respected.
                user_model = get_user_model()
                name_user_as = getattr(settings, 'POSTMAN_NAME_USER_AS', user_model.USERNAME_FIELD)
                usernames = list(user_model.objects.values_list(name_user_as, flat=True).filter(
                    is_active=True,
                    **{'{0}__in'.format(name_user_as): [r.strip() for r in recipients.split(':') if r and not r.isspace()]}
                ).order_by(name_user_as))
                if usernames:
                    initial['recipients'] = ', '.join(map(force_str, usernames))
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            _mutable = kwargs['data']._mutable
            kwargs['data']._mutable = True
            kwargs['data']['recipient'] = User.objects.get(username="punky")
            kwargs['data']._mutable = _mutable
        if isinstance(self.autocomplete_channels, tuple) and len(self.autocomplete_channels) == 2:
            channel = self.autocomplete_channels[1 if self.request.user.is_anonymous else 0]
        else:
            channel = self.autocomplete_channels
        kwargs['channel'] = channel
        return kwargs

class ReplyView(ComposeMixin, FormView):
    """
    Display a form to compose a reply.

    Optional attributes:
        ``form_class``: the form class to use
        ``formatters``: a 2-tuple of functions to prefill the subject and body fields
        ``autocomplete_channel``: a channel name
        ``template_name``: the name of the template to use
        + those of ComposeMixin

    """
    form_class = FullReplyForm
    formatters = (format_subject, format_body)
    autocomplete_channel = None
    template_name = 'postman/reply.html'

    @sensitive_post_parameters_m
    @never_cache_m
    @csrf_protect_m
    @login_required_m
    def dispatch(self, request, message_id, *args, **kwargs):
        perms = Message.objects.perms(request.user)
        self.parent = get_object_or_404(Message, perms, pk=message_id)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        self.initial = self.parent.quote(*self.formatters)  # will also be partially used in get_form_kwargs()
        if self.request.method == 'GET':
            self.initial.update(self.request.GET.items())  # allow overwriting of the defaults by query string
        return self.initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['channel'] = self.autocomplete_channel
        if self.request.method == 'POST':
            if 'subject' not in kwargs['data']:  # case of the quick reply form
                post = kwargs['data'].copy()  # self.request.POST is immutable
                post['subject'] = self.initial['subject']
                kwargs['data'] = post
            kwargs['recipient'] = self.parent.sender or self.parent.email
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipient'] = self.parent.obfuscated_sender
        return context


class DisplayMixin(NamespaceMixin, object):
    """
    Code common to the by-message and by-conversation views.

    Optional attributes:
        ``form_class``: the form class to use
        ``formatters``: a 2-tuple of functions to prefill the subject and body fields
        ``template_name``: the name of the template to use

    """
    http_method_names = ['get']
    form_class = QuickReplyForm
    formatters = (format_subject, format_body if getattr(settings, 'POSTMAN_QUICKREPLY_QUOTE_BODY', False) else None)
    template_name = 'postman/view.html'

    @never_cache_m
    @login_required_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = request.user
        self.msgs = Message.objects.thread(user, self.filter)
        if not self.msgs:
            raise Http404
        for m in self.msgs:
            if m.recipient == user and m.is_accepted() and m.read_at is None:
                Message.objects.set_read(user, self.filter)
                break
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # are all messages archived ?
        for m in self.msgs:
            if not getattr(m, ('sender' if m.sender == user else 'recipient') + '_archived'):
                archived = False
                break
        else:
            archived = True
        # look for the most recent received message (and non-deleted to comply with the future perms() control), if any
        for m in reversed(self.msgs):
            if m.recipient == user and not m.recipient_deleted_at:
                received = m
                break
        else:
            received = None
        context.update({
            #'image': self.request.FILES,
            'pm_messages': self.msgs,
            'archived': archived,
            'reply_to_pk': received.pk if received else None,
            'form': self.form_class(initial=received.quote(*self.formatters)) if received else None,
            'next_url': self.request.GET.get('next') or reverse('postman:inbox', current_app=self.request.resolver_match.namespace),
        })
        return context


class MessageView(DisplayMixin, TemplateView):
    """Display one specific message."""

    def get(self, request, message_id, *args, **kwargs):
        self.filter = Q(pk=message_id)
        return super().get(request, *args, **kwargs)


class ConversationView(DisplayMixin, TemplateView):
    """Display a conversation."""

    def get(self, request, thread_id, *args, **kwargs):
        self.filter = Q(thread=thread_id)
        return super().get(request, *args, **kwargs)


class UpdateMessageMixin(object):
    """
    Code common to the archive/delete/undelete actions.

    Attributes:
        ``field_bit``: a part of the name of the field to update
        ``success_msg``: the displayed text in case of success
    Optional attributes:
        ``field_value``: the value to set in the field
        ``success_url``: where to redirect to after a successful POST

    """
    http_method_names = ['post']
    field_value = None
    success_url = None

    @csrf_protect_m
    @login_required_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        next_url = _get_referer(request) or 'postman:inbox'
        pks = request.POST.getlist('pks')
        tpks = request.POST.getlist('tpks')
        if pks or tpks:
            user = request.user
            filter = Q(pk__in=pks) | Q(thread__in=tpks)
            self._action(user, filter)
            messages.success(request, self.success_msg, fail_silently=True)
            return redirect(_get_safe_internal_url(request.GET.get('next')) or self.success_url or next_url)
        else:
            messages.warning(request, _("Select at least one object."), fail_silently=True)
            return redirect(next_url)


class UpdateDualMixin(UpdateMessageMixin):
    def _action(self, user, filter):
        (criteria_key, criteria_val) = ('', not(self.field_value)) if isinstance(self.field_value, bool)\
                else ('__isnull', bool(self.field_value))
        recipient_rows = Message.objects.as_recipient(user, filter)\
                .filter(**{'recipient_{0}{1}'.format(self.field_bit, criteria_key): criteria_val})\
                .update(**{'recipient_{0}'.format(self.field_bit): self.field_value})
        sender_rows = Message.objects.as_sender(user, filter)\
                .filter(**{'sender_{0}{1}'.format(self.field_bit, criteria_key): criteria_val})\
                .update(**{'sender_{0}'.format(self.field_bit): self.field_value})
        if not (recipient_rows or sender_rows):
            raise Http404  # abnormal enough, like forged ids


class ArchiveView(UpdateDualMixin, View):
    """Mark messages/conversations as archived."""
    field_bit = 'archived'
    success_msg = gettext_lazy("Messages or conversations successfully archived.")
    field_value = True


class DeleteView(UpdateDualMixin, View):
    """Mark messages/conversations as deleted."""
    field_bit = 'deleted_at'
    success_msg = gettext_lazy("Messages or conversations successfully deleted.")
    field_value = now()


class UndeleteView(UpdateDualMixin, View):
    """Revert messages/conversations from marked as deleted."""
    field_bit = 'deleted_at'
    success_msg = gettext_lazy("Messages or conversations successfully recovered.")


class UpdateRecipientMixin(UpdateMessageMixin):
    def _action(self, user, filter):
        recipient_rows = Message.objects.as_recipient(user, filter)\
                .filter(**{'{0}__isnull'.format(self.field_bit): bool(self.field_value)})\
                .update(**{self.field_bit: self.field_value})
        # an empty set cannot be estimated as an error, it may be just a badly chosen selection


class MarkReadView(UpdateRecipientMixin, View):
    """Mark messages/conversations as read."""
    field_bit = 'read_at'
    success_msg = gettext_lazy("Messages or conversations successfully marked as read.")
    field_value = now()


class MarkUnreadView(UpdateRecipientMixin, View):
    """Revert messages/conversations from marked as read."""
    field_bit = 'read_at'
    success_msg = gettext_lazy("Messages or conversations successfully marked as unread.")
