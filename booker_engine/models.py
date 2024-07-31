from django.db import models

class  Booking(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return f'ID:{self.id}, {self.name}, Date:{self.start.strftime("%d/%m/%Y")}, Start:{self.start.strftime("%H:%M")}, End:{self.end.strftime("%H:%M")}'

