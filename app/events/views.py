from calendar import Calendar
from collections import defaultdict
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import EventForm
from .models import Event, EventSubscription


@login_required
def list_events(request):
    today = timezone.localdate()
    current_month = today.replace(day=1)
    month = request.GET.get("month", current_month.strftime("%Y-%m"))
    try:
        month_start = date.fromisoformat(f"{month}-01")
    except ValueError as error:
        raise Http404("Month must be in YYYY-MM format.") from error
    # Leave room for adjacent dates in the grid and timezone conversion.
    if not 2 <= month_start.year <= 9998:
        raise Http404("Month is outside the calendar range.")

    category = request.GET.get("category", "")
    if category and category not in Event.Category.values:
        raise Http404("Unknown event category.")

    next_month = (month_start + timedelta(days=32)).replace(day=1)
    previous_month = (month_start - timedelta(days=1)).replace(day=1)
    start = timezone.make_aware(datetime.combine(month_start, time.min))
    end = timezone.make_aware(datetime.combine(next_month, time.min))

    events = Event.objects.select_related("submitted_by")
    if category:
        events = events.filter(category=category)
    scheduled = events.filter(starts_at__gte=start, starts_at__lt=end).order_by(
        "starts_at", "pk"
    )
    events_by_day = defaultdict(list)
    for event in scheduled:
        events_by_day[timezone.localdate(event.starts_at)].append(event)

    weeks = [
        [
            {
                "date": day,
                "events": events_by_day.get(day, ()),
                "in_month": day.month == month_start.month,
            }
            for day in week
        ]
        for week in Calendar().monthdatescalendar(month_start.year, month_start.month)
    ]
    return render(
        request,
        "events/calendar.html",
        {
            "today": today,
            "month_start": month_start,
            "previous_month": previous_month if previous_month.year >= 2 else None,
            "next_month": next_month if next_month.year <= 9998 else None,
            "category": category,
            "categories": Event.Category.choices,
            "weeks": weeks,
            "agenda": list(events_by_day.items()),
            "unscheduled": events.filter(starts_at__isnull=True).order_by("-pk"),
        },
    )


@login_required
def event_form(request, pk=None):
    event = None
    if pk is not None:
        event = get_object_or_404(Event, pk=pk, submitted_by=request.user)
    data = request.POST if request.method == "POST" else None
    form = EventForm(data, instance=event)
    if request.method == "POST" and form.is_valid():
        saved_event = form.save(commit=False)
        saved_event.submitted_by = request.user
        saved_event.save()
        messages.success(request, "Event updated." if event else "Event added.")
        event_day = timezone.localdate(saved_event.starts_at)
        return redirect(
            reverse(
                "event_list",
                query={"month": event_day.isoformat()[:7]},
                fragment=f"event-{saved_event.pk}",
            )
        )
    return render(request, "events/form.html", {"form": form, "event": event})


@login_required
def subscriptions(request):
    followed = set(
        EventSubscription.objects.filter(user=request.user).values_list(
            "category", flat=True
        )
    )
    feed = (
        Event.objects.filter(category__in=followed, starts_at__gte=timezone.now())
        .select_related("submitted_by")
        .order_by("starts_at", "pk")
    )
    return render(
        request,
        "events/subscriptions.html",
        {
            "categories": Event.Category.choices,
            "followed": followed,
            "page_obj": Paginator(feed, 12).get_page(request.GET.get("page")),
        },
    )


@login_required
@require_POST
def update_subscription(request, category):
    if category not in Event.Category.values:
        raise Http404("Unknown event category.")
    action = request.POST.get("action")
    if action == "follow":
        EventSubscription.objects.get_or_create(user=request.user, category=category)
        messages.success(request, f"Following {Event.Category(category).label}.")
    elif action == "unfollow":
        EventSubscription.objects.filter(user=request.user, category=category).delete()
        messages.success(request, f"Unfollowed {Event.Category(category).label}.")
    else:
        return HttpResponseBadRequest("Choose follow or unfollow.")
    return redirect("event_subscriptions")
