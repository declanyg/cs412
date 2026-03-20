# File: models.py
# Author: Declan Young (declanyg@bu.edu), 3/19/2026
# Description: models file for voter_analytics app

import csv
import datetime
from django.db import models
from datetime import date

# Create your models here.
class Voter(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    registration_date = models.DateField()
    party_affiliation = models.CharField(max_length=100)
    precinct_number = models.CharField(max_length=20)

    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)

    voter_score = models.IntegerField(default=0)

    @classmethod
    def load_data(cls, file_path):
        with open(file_path, newline='') as f:
            reader = csv.reader(f)
            next(reader)
            
            for row in reader:
                try:
                    voter = cls.objects.create(
                        last_name=row[1],
                        first_name=row[2],
                        date_of_birth=date.fromisoformat(row[7]),
                        registration_date=date.fromisoformat(row[8]),
                        party_affiliation=row[9],
                        precinct_number=row[10],

                        v20state=True if row[11] == "TRUE" else False,
                        v21town=True if row[12] == "TRUE" else False,
                        v21primary=True if row[13] == "TRUE" else False,
                        v22general=True if row[14] == "TRUE" else False,
                        v23town=True if row[15] == "TRUE" else False,
                        voter_score=int(row[16])
                    )

                    Residential_Address.objects.create(
                        voter=voter,
                        street_number=row[3],
                        street_name=row[4],
                        apartment_number=row[5],
                        zip_code=row[6],
                    )
                except ValueError as e:
                    print(f"Error occurred while processing row: {row}")
                    print(f"Error message: {e}")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.date_of_birth})"

class Residential_Address(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='residential_addresses')
    street_number = models.CharField(max_length=20)
    street_name = models.CharField(max_length=100)
    apartment_number = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=10)