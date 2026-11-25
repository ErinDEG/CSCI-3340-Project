from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnnouncementForm
from .models import Announcement


def board(request):
    announcements = Announcement.objects.select_related("author")
    page = Paginator(announcements, 10).get_page(request.GET.get("page"))
    return render(request, "bulletin/board.html", {"page_obj": page})


@login_required
def announcement_form(request, pk=None):
    announcement = None
    if pk is not None:
        announcement = get_object_or_404(Announcement, pk=pk, author=request.user)
    data = request.POST if request.method == "POST" else None
    form = AnnouncementForm(data, instance=announcement)
    if request.method == "POST" and form.is_valid():
        saved_announcement = form.save(commit=False)
        saved_announcement.author = request.user
        saved_announcement.save()
        messages.success(
            request, "Announcement updated." if announcement else "Announcement posted."
        )
        return redirect("bulletin:board")
    return render(
        request, "bulletin/form.html", {"form": form, "announcement": announcement}
    )
