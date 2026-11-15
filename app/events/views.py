from django.shortcuts import render, redirect
# Create your views here.
from django.contrib.auth.decorators import login_required
from .forms import EventForm
from .models import Event



#    This will be for when you add an event
@login_required
def add_events(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.submitted_by = request.user
            event.save()
            return redirect("event_list")
    else:
        form = EventForm()

    return render(request, 'add_event.html')

@login_required
def list_events(request):
    events = Event.objects.all()
    return render(request, 'index.html', {'events': events})


