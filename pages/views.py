from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.db.models import Max, Count, F
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.contrib import messages
from .models import Users, Exercises, ExerciseTypes, Classes, PRRecords, Comments
from .forms import LoginForm, RegisterForm, ExerciseForm, ExerciseEditForm, ExerciseTypeAddForm, CommentForm
from django.contrib.auth.hashers import make_password, check_password


def require_login(request):
    if not request.session.get("user_id"):
        return HttpResponseForbidden("Kirjautuminen vaaditaan")
    return None

def index(request):
    exercises = (
        Exercises.objects.select_related("user", "exercise_type", "exercise_class")
        .filter(public=1)
        .annotate(
            username=F("user__username"),
            exercise_type_name=F("exercise_type__exercise_type_name"),
            label=F("exercise_class__label"),
        )
        .values(
            "id",
            "user_id",
            "username",
            "exercise_type_name",
            "label",
            "exercise_weight",
            "exercise_date",
            "note",
            "comment_count",
        )
        .order_by("-exercise_date")
    )
    return render(request, "index.html", {"exercises": exercises})


@csrf_protect
def register(request):
    if request.method == "GET":
        return render(request, "register.html", {"form": RegisterForm()})
    form = RegisterForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Error: invalid input")
        return redirect("register")
    username = form.cleaned_data["username"]
    p1 = form.cleaned_data["password1"]
    p2 = form.cleaned_data["password2"]
    public = 1 if form.cleaned_data.get("public") else 0
    if p1 != p2:
        messages.error(request, "Error: passwords don't match")
        return redirect("register")
    if Users.objects.filter(username=username).exists():
        messages.error(request, "Error: username exists")
        return redirect("register")

    '''
    FLAW 2: A02:2021 Cryptographic Failures. Password is saved in plain text and anyone with a right access can read it directly.

    FIX 2: Use password hasher from Django-library
    # safe_hash = make_password(p1)
    # user = Users(username=username, password_hash=safe_hash, default_public=public, etc...)
    '''

    user = Users(
        username=username,
        password_hash=p1,  # FLAW 2!
        default_public=public,
        created=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
        user_exercise_count=0,
        user_comment_count=0,
    )
    user.save(force_insert=True)

    user = Users.objects.get(username=username)
    for name in ["Bench press", "Deadlift", "Back squat"]:
        ExerciseTypes(user=user, exercise_type_name=name).save(force_insert=True)

    return render(request, "register_success.html")


@csrf_protect
def login_view(request):

    '''
    FLAW 3: A07:2021 Identification & Authentication Failures
    No rate limiting, lockout, or delay, which enables brute force.

    FIX 3: add a small delay and calculate failed attempts

    from django.core.cache import cache
    import time
    ip = request.META.get("REMOTE_ADDR", "unknown")
    key = f"login_fail:{ip}"
    fails = cache.get(key, 0)
    if fails >= 5:
        return HttpResponse("Too many attempts. Go away")
    time.sleep(1)  # small delay to slow automated guessing
    '''

    '''
    FLAW 4: A09:2021 Security Logging and Monitoring Failures
    No logging for failed/successful logins, so no forensics or analytics available.

    FIX 4: logging. add explicit auth logs with username and IP.
    import logging
    log = logging.getLogger(__name__)
    if failed: log.warning("Auth failed user=%s ip=%s", username, ip)
    if success: log.info("Auth success user=%s ip=%s", username, ip)
    '''

    if request.method == "GET":
        return render(request, "login.html", {"form": LoginForm()})
    form = LoginForm(request.POST)
    if not form.is_valid():
        return render(request, "login.html", {"form": form})
    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]

    user = Users.objects.filter(username=username).first()

    '''
    FLAW 2: A02:2021 Cryptographic Failures
    Authentication uses password in plain text

    FIX 2: Verify using check_password() from Django library
    # if user and check_password(password, user.password_hash):
    '''

    if user and user.password_hash == password:
        request.session["user_id"] = user.id
        return redirect("index")

    messages.error(request, "Error: wrong username or password")
    return render(request, "login.html", {"form": form})


def logout_view(request):
    request.session.pop("user_id", None)
    return redirect("index")


@csrf_protect
def new_exercise(request):
    if (resp := require_login(request)):
        return resp
    me = Users.objects.get(id=request.session["user_id"])
    if request.method == "GET":
        types = ExerciseTypes.objects.filter(user=me).order_by("exercise_type_name")
        classes = Classes.objects.all().order_by("id")
        default = me.default_public
        return render(request, "new_exercise.html", {"types": types, "classes": classes, "default": default, "form": ExerciseForm()})
    form = ExerciseForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Error: invalid input")
        return redirect("new_exercise")
    type_id = form.cleaned_data["type_id"]
    class_id = form.cleaned_data["class_id"]
    weight = form.cleaned_data["weight"]
    ex_date = form.cleaned_data["date"]
    note = form.cleaned_data.get("note") or ""
    public = 1 if form.cleaned_data.get("public") else 0
    et = get_object_or_404(ExerciseTypes, id=type_id, user=me)
    cl = get_object_or_404(Classes, id=class_id)
    ex = Exercises(user=me, exercise_type=et, exercise_class=cl, exercise_weight=weight, exercise_date=ex_date, public=public, note=note, comment_count=0)
    ex.save(force_insert=True)
    reps = cl.reps
    e1rm_epley = int(weight * (1 + reps / 30))
    e1rm_lombardi = int(weight * (reps ** 0.10))
    e1rm_brzycki = int(weight * 36 / (37 - reps))
    PRRecords(user=me, exercise_type=et, exercise_class=cl, e1rm_epley=e1rm_epley, e1rm_lombardi=e1rm_lombardi, e1rm_brzycki=e1rm_brzycki, ex_weight=weight, pr_date=ex_date).save(force_insert=True)
    me.user_exercise_count += 1
    me.save(update_fields=["user_exercise_count"])
    return redirect("index")

def exercises(request):
    if (resp := require_login(request)): return resp
    me = Users.objects.get(id=request.session["user_id"])
    exercises_qs = (
        Exercises.objects.select_related("exercise_type", "exercise_class")
        .filter(user=me)
        .annotate(
            username=F("user__username"),
            exercise_type_name=F("exercise_type__exercise_type_name"),
            label=F("exercise_class__label"),
        )
        .values(
            "id","user_id","username","exercise_type_name","label",
            "exercise_weight","exercise_date","note","comment_count",
        )
        .order_by("-exercise_date")
    )
    types = ExerciseTypes.objects.filter(user=me).order_by("exercise_type_name")
    return render(request, "exercises.html", {"exercises": exercises_qs, "types": types})

@csrf_protect
def edit_exercise(request, exercise_id: int):
    if (resp := require_login(request)):
        return resp
    
    ex = get_object_or_404(Exercises, id=exercise_id)
    me = Users.objects.get(id=request.session["user_id"])

    '''
    FLAW 1. A01:2021-Broken Access Control - No ownership check. It is possible that another user can update other users exercise!
    FIX 1. Check if the the owner of the exericse is the same as the logged-in user. If not, return error code 403
    
    if ex.user_id != me.id:
        return HttpResponseForbidden("403")
    '''
    if request.method == "GET":
        types = ExerciseTypes.objects.filter(user=me).order_by("exercise_type_name")
        return render(request, "edit.html", {"exercise": ex, "types": types, "form": ExerciseEditForm(initial={"type_id": ex.exercise_type_id, "weight": ex.exercise_weight, "date": ex.exercise_date, "note": ex.note or ""})})
    form = ExerciseEditForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Error: invalid input")
        return redirect("edit_exercise", exercise_id=exercise_id)
    
    type_id = form.cleaned_data["type_id"]
    weight = form.cleaned_data["weight"]
    date = form.cleaned_data["date"]
    note = form.cleaned_data.get("note") or ""

    et = get_object_or_404(ExerciseTypes, id=type_id, user=me)
    ex.exercise_type = et
    ex.exercise_weight = weight
    ex.exercise_date = date
    ex.note = note
    ex.save(update_fields=["exercise_type", "exercise_weight", "exercise_date", "note"])
    return redirect("index")

@csrf_protect
def remove_exercise(request, exercise_id: int):
    if (resp := require_login(request)):
        return resp
    ex = get_object_or_404(Exercises, id=exercise_id)
    me = Users.objects.get(id=request.session["user_id"])
    if ex.user_id != me.id:
        return HttpResponseForbidden("403")
    if request.method == "GET":
        return render(request, "remove.html", {"exercise": ex})
    if "remove" in request.POST:
        ex.delete()
        me.user_exercise_count -= 1
        me.save(update_fields=["user_exercise_count"])
        return redirect("exercises")
    return redirect("index")

@csrf_protect
def exercise_types(request):
    if (resp := require_login(request)):
        return resp
    me = Users.objects.get(id=request.session["user_id"])
    types = list(ExerciseTypes.objects.filter(user=me).order_by("exercise_type_name"))
    if request.method == "GET":
        return render(request, "edit_exercise_types.html", {"types": types, "form": ExerciseTypeAddForm()})
    if "delete_id" in request.POST:
        try:
            type_id = int(request.POST.get("delete_id"))
        except (TypeError, ValueError):
            return redirect("exercise_types")
        t = next((x for x in types if x.id == type_id), None)
        if not t or t.user_id != me.id:
            return HttpResponseForbidden("403")
        t.delete()
    elif "name" in request.POST:
        form = ExerciseTypeAddForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"].strip()
            if name:
                ExerciseTypes(user=me, exercise_type_name=name).save(force_insert=True)
    return redirect("exercise_types")

def search(request):
    if (resp := require_login(request)): return resp
    me = Users.objects.get(id=request.session["user_id"])
    try:
        type_id = int(request.GET.get("type_id")) if request.GET.get("type_id") else None
    except (TypeError, ValueError):
        type_id = None
    exercises_qs = Exercises.objects.select_related("exercise_type","exercise_class").filter(user=me)
    if type_id:
        exercises_qs = exercises_qs.filter(exercise_type_id=type_id)
    exercises_qs = (
        exercises_qs
        .annotate(
            username=F("user__username"),
            exercise_type_name=F("exercise_type__exercise_type_name"),
            label=F("exercise_class__label"),
        )
        .values(
            "id","user_id","username","exercise_type_name","label",
            "exercise_weight","exercise_date","note","comment_count",
        )
        .order_by("-exercise_date")
    )
    types = ExerciseTypes.objects.filter(user=me).order_by("exercise_type_name")
    return render(request, "exercises.html", {"exercises": exercises_qs, "types": types, "selected_type_id": type_id})

@csrf_protect
def comments(request, exercise_id: int):
    if (resp := require_login(request)):
        return resp
    me = Users.objects.get(id=request.session["user_id"])
    ex = get_object_or_404(Exercises, id=exercise_id)
    comments_qs = Comments.objects.select_related("user").filter(exercise=ex).order_by("-created_date")
    if request.method == "GET":
        return render(request, "comments.html", {"exercise": ex, "comments": comments_qs, "form": CommentForm()})
    form = CommentForm(request.POST)
    if form.is_valid():
        text = form.cleaned_data["comment"].strip()
        if text:
            Comments(exercise=ex, user=me, comment_text=text, created_date=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")).save(force_insert=True)
            ex.comment_count = (ex.comment_count or 0) + 1
            ex.save(update_fields=["comment_count"])
            me.user_comment_count = (me.user_comment_count or 0) + 1
            me.save(update_fields=["user_comment_count"])
    return redirect("comments", exercise_id=exercise_id)

def stats(request):
    if (resp := require_login(request)):
        return resp
    me = Users.objects.get(id=request.session["user_id"])
    stats_qs = Exercises.objects.filter(user=me).select_related("exercise_type", "exercise_class").values("exercise_type__exercise_type_name", "exercise_class__label").annotate(max_weight=Max("exercise_weight"), lift_count=Count("id"), last_date=Max("exercise_date")).order_by("exercise_type__exercise_type_name", "exercise_class__label")
    latest_by_type = {}
    for pr in PRRecords.objects.filter(user=me).select_related("exercise_type").order_by("exercise_type__exercise_type_name", "-pr_date"):
        key = pr.exercise_type_id
        if key not in latest_by_type:
            latest_by_type[key] = pr
    pr_list = list(latest_by_type.values())

    stats_dict = defaultdict(list)
    for row in stats_qs:
        stats_dict[row["exercise_type__exercise_type_name"]].append({
            "class_label": row["exercise_class__label"],
            "max_weight": row["max_weight"],
            "lift_count": row["lift_count"],
            "last_date": row["last_date"],
        })
    return render(request, "stats.html", {"stats": dict(stats_dict),"pr": pr_list})

def user_page(request, user_id=None):
    if user_id is None:
        if (resp := require_login(request)):
            return resp
        user_id = request.session["user_id"]
    user = get_object_or_404(Users, id=user_id)
    last_ex = Exercises.objects.filter(user=user).order_by("-exercise_date").values_list("exercise_date", flat=True).first()
    last_exercise = last_ex or "No exercises yet"
    context = {"user": {"username": user.username, "created": user.created, "user_exercise_count": user.user_exercise_count, "user_comment_count": user.user_comment_count, "last_exercise": last_exercise}}
    return render(request, "user.html", context)
