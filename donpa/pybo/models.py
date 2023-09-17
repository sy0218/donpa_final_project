from django.db import models


class DonpaItem1(models.Model):
    item_img = models.TextField(blank=True, null=True)
    item_name = models.TextField(blank=True, null=False, primary_key=True)  # null=False로 수정
    price = models.FloatField(blank=True, null=True)
    before_now = models.FloatField(blank=True, null=True)
    before_one = models.FloatField(blank=True, null=True)
    before_two = models.FloatField(blank=True, null=True)
    before_three = models.FloatField(blank=True, null=True)
    before_four = models.FloatField(blank=True, null=True)
    before_five = models.FloatField(blank=True, null=True)
    before_six = models.FloatField(blank=True, null=True)
    before_seven = models.FloatField(blank=True, null=True)
    before_eight = models.FloatField(blank=True, null=True)
    before_nine = models.FloatField(blank=True, null=True)
    before_ten = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'donpa_item1'


class DonpaNews(models.Model):
    photo = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=False, primary_key=True)

    class Meta:
        managed = False
        db_table = 'donpa_news'


class DonpaEvent(models.Model):
    img = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    herf = models.TextField(blank=True, null=False, primary_key=True)

    class Meta:
        managed = False
        db_table = 'donpa_event'


class InputList(models.Model):
    title = models.TextField(blank=True, null=False, primary_key=True)
    jobname = models.TextField(blank=True, null=True)
    emblem = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'input_list'


class InputList1(models.Model):
    title = models.TextField(blank=True, null=False, primary_key=True)
    jobname = models.TextField(blank=True, null=True)
    emblem = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'input_list1'


class Goldprice(models.Model):
    date = models.TextField(blank=True, null=False, primary_key=True)
    sell = models.FloatField(blank=True, null=True)
    buy = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'goldprice'