from django.db import models

# Create your models here.
class fileDoc(models.Model):
    id = models.AutoField(primary_key=True)
    file_id = models.CharField(max_length=256)
    name=models.CharField(max_length=256,null=True)
    size=models.IntegerField()
    url=models.CharField(max_length=256)
    file = models.FileField() # config match field(regex for only allowing png or pdf or jpg files)

    def __str__(self):
        return self.name
