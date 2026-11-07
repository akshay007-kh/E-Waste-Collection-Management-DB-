
from django.db import models


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.category_name


class CollectionCentre(models.Model):
    centre_name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.centre_name


class Staff(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    password = models.CharField(max_length=128, default='')
    view_pass = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.name


class User(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    password = models.CharField(max_length=128, default='')
    view_pass = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.name


class CollectionRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    centre = models.ForeignKey(
        CollectionCentre, on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    weight = models.FloatField()
    pickup_address = models.TextField()
    pickup_date = models.DateField()
    status = models.CharField(
        max_length=20, default="Pending"
    )

    def __str__(self):
        return f"Request {self.id}"


class Assignment(models.Model):
    request = models.ForeignKey(
        CollectionRequest, on_delete=models.CASCADE
    )
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE
    )
    assigned_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20, default="Assigned"
    )


class Collection(models.Model):
    request = models.ForeignKey(
        CollectionRequest, on_delete=models.CASCADE
    )
    actual_weight = models.FloatField()
    collection_date = models.DateField()
    status = models.CharField(
        max_length=20, default="Collected"
    )


class Recycling(models.Model):
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE
    )
    recycled_weight = models.FloatField()
    recycling_date = models.DateField()
    status = models.CharField(
        max_length=20, default="Processing"
    )


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request = models.ForeignKey(
        CollectionRequest, on_delete=models.CASCADE
    )
    rating = models.PositiveIntegerField()
    message = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id}"
