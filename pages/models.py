from django.db import models

class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.TextField(unique=True)
    password_hash = models.TextField()
    default_public = models.IntegerField()
    created = models.TextField()
    user_exercise_count = models.IntegerField()
    user_comment_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self):
        return self.username


class ExerciseTypes(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="user_id")
    exercise_type_name = models.TextField()

    class Meta:
        managed = False
        db_table = "exercise_types"

    def __str__(self):
        return self.exercise_type_name


class Classes(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.TextField()
    reps = models.IntegerField()

    class Meta:
        managed = False
        db_table = "classes"

    def __str__(self):
        return self.label


class Exercises(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="user_id")
    exercise_type = models.ForeignKey(ExerciseTypes, on_delete=models.CASCADE, db_column="exercise_type_id")
    exercise_class = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True, db_column="exercise_class_id")
    exercise_weight = models.FloatField()
    exercise_date = models.TextField()
    public = models.IntegerField()
    note = models.TextField(null=True)
    comment_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = "exercises"


class PRRecords(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="user_id")
    exercise_type = models.ForeignKey(ExerciseTypes, on_delete=models.CASCADE, db_column="exercise_type_id")
    exercise_class = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True, db_column="exercise_class_id")
    e1rm_epley = models.FloatField()
    e1rm_lombardi = models.FloatField()
    e1rm_brzycki = models.FloatField()
    ex_weight = models.FloatField()
    pr_date = models.TextField()

    class Meta:
        managed = False
        db_table = "pr_records"


class Comments(models.Model):
    id = models.IntegerField(primary_key=True)
    exercise = models.ForeignKey(Exercises, on_delete=models.CASCADE, db_column="exercise_id")
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="user_id")
    comment_text = models.TextField()
    created_date = models.TextField()

    class Meta:
        managed = False
        db_table = "comments"