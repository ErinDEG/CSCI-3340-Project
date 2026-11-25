**Campus Hub**
=
## Campus events and bulletin board

Campus Hub includes student accounts, a campus event calendar, and a public bulletin board. [User stories and acceptance criteria](docs/user-stories.md)

### Run locally

From the repository root, create a virtual environment using Python 3.10 or newer.

```sh
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS or Linux, or `\.venv\Scripts\Activate.ps1` in Windows PowerShell. Then install the requirements and start Django.

```sh
python -m pip install -r requirements.txt
python app/manage.py migrate
python app/manage.py runserver
```

Dates and times use the campus time zone. Set the `CAMPUS_TIME_ZONE` environment variable to change the default of `America/Chicago`.

### Demo walkthrough

1. Open the [home page](http://127.0.0.1:8000/) and create an account.
2. Choose **Campus events**, then **Add an event**. Pick a category and a future start time. Enter a full venue name and address so **View map** can find the location in Google Maps.
3. Find your event on the calendar and in the agenda below it. Try filtering the month by category. If an older event has no date, look under **Events without a date**. Its author can add a date and category.
4. Open **My subscriptions** and follow your event’s category. Your event appears in the upcoming feed. Unfollow the category to remove its events from the feed.
5. Open **Bulletin board** and post an announcement. Check that it appears at the top and that you can edit it. Log out and reopen the board to see what guests can read.

Run the feature and account tests with `python app/manage.py test core events bulletin`.


**Description**
-
Campus Hub is a web app designed to help campus students connect, collaborate, and share resources within their community. This includes, but not limited to, organizing study groups and sessions, organizing and discovering campus events,
reporting lost items, and borrowing/renting items from other students. 


**Objectives**

- Help students connect through posts, comments, and study groups.
- Make it easier to find study partners by subject or course or general groups.
- Provide a space for students to organize and discover campus events.
- Help students recover lost items through searchable listings.
- Support borrowing and renting items for an agreed period.


### Post creations

  - Allow students to create and modify their own posts
  - Students are able to react/comment on posts
  

### Study Groups

Allow students to:

  - Create study groups organized by subject/course
  - Browse available groups
  - Join/leave groups
  - Group management
  - Notifications on planned groups depending on subject or course.

### Lost/Found Reports

If an item is missing

  - A student can report where they might've lost it and when it was realized to be missing.

When the item is found, with or without a previous post
  
  - The student can either send an image of where it was found, and or respond with the location/building/organization it was given to for pickup.

### Campus Events

Students and Organizations can post their upcoming events, with its location, time, and description as long as it's within the campus area.

### Renting/Borrowing Items

Students can list items for others to borrow during their semester. These items can be listed as books, calculators, etc. Students who list their items have the option for it to be free or set at a pay rate.

Transactions are not done through the website, and must be ONLY in-person. When a listing is currently borrowed/rented, the listing is hidden for viewing.

This ensures that all listings are available, and not flooded with other listings that are currently in-use.

## Agile Planning

Our group plans to work on the app in sprints instead of building everything at once. Each sprint will last about a week and will be at the start of the week. We will choose what to work on and split the tasks between our group members.

At the end of each week we will go over what we finished, any problems found, and what needs work. We will also use this to prepare for our class updates and this plan might change as we learn more about Django and see how long each feature takes to build.

Our priorities for now are:

- Planning the pages and how students will use the app.
- Creating the home page.
- Adding accounts, login, and student profiles.
- Adding study groups that students can create and join.

After the basic features work, we will add features like comments, campus events, lost and found listings, and borrowing or renting items. 

### Sprint Plan

Sprint 1 : Agree on the main requirements, write our user stories, and sketch the home page and account pages. Then start with diagrams to help us plan how the app will work.

