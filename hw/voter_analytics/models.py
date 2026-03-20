import csv
import datetime
from django.db import models

# Create your models here.
class Voter(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    registration_date = models.DateField()
    party_affiliation = models.CharField(max_length=100)
    precinct_number = models.CharField(max_length=20)

    v20state = models.CharField(max_length=2)
    v21town = models.CharField(max_length=100)
    v21primary = models.CharField(max_length=100)
    v22general = models.CharField(max_length=100)
    v23town = models.CharField(max_length=100)

    @classmethod
    def load_data(cls, file_path):
        with open(file_path, newline='') as f:
            reader = csv.reader(f)

            for row in reader:
                voter = cls.objects.create(
                    last_name=row[1],
                    first_name=row[2],
                    date_of_birth=datetime.strptime(row[7], "%m/%d/%Y").date(),
                    registration_date=datetime.strptime(row[8], "%m/%d/%Y").date(),
                    party_affiliation=row[9],
                    precinct_number=row[10],

                    v20state=row[11],
                    v21town=row[12],
                    v21primary=row[13],
                    v22general=row[14],
                    v23town=row[15],
                )

                Residential_Address.objects.create(
                    voter=voter,
                    street_number=row[3],
                    street_name=row[4],
                    apartment_number=row[5],
                    zip_code=row[6],
                )

class Residential_Address(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='residential_addresses')
    street_number = models.CharField(max_length=20)
    street_name = models.CharField(max_length=100)
    apartment_number = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=10)