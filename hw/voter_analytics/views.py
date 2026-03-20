# File: views.py
# Author: Declan Young (declanyg@bu.edu), 3/19/2026
# Description: views file for voter_analytics app

from django.shortcuts import render

from django.views.generic import ListView, DetailView
from .models import Residential_Address, Voter

import plotly.graph_objs as go
from plotly.offline import plot
from collections import Counter

# Create your views here.
class VoterAnalyticsView(ListView):
    model = Voter
    template_name = 'voter_analytics/voters.html'
    context_object_name = 'voters'
    paginate_by = 100

    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request

        if request.GET.get("party"):
            qs = qs.filter(party_affiliation__startswith=request.GET["party"])

        if request.GET.get("min_year"):
            qs = qs.filter(date_of_birth__year__gte=request.GET["min_year"])

        if request.GET.get("max_year"):
            qs = qs.filter(date_of_birth__year__lte=request.GET["max_year"])

        if request.GET.get("score"):
            qs = qs.filter(voter_score=request.GET["score"])
        
        if request.GET.get("v20state") == "1":
            qs = qs.filter(v20state=True)

        if request.GET.get("v21town") == "1":
            qs = qs.filter(v21town=True)

        if request.GET.get("v21primary") == "1":
            qs = qs.filter(v21primary=True)

        if request.GET.get("v22general") == "1":
            qs = qs.filter(v22general=True)

        if request.GET.get("v23town") == "1":
            qs = qs.filter(v23town=True)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["years"] = range(1900, 2025)
        return context

class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["residential_addresses"] = self.object.residential_addresses.first()
        return context

class VoterGraphsView(ListView):
    model = Voter
    template_name = "voter_analytics/graphs.html"
    context_object_name = "voters"

    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request

        if request.GET.get("party"):
            qs = qs.filter(party_affiliation__startswith=request.GET["party"])

        if request.GET.get("min_year"):
            qs = qs.filter(date_of_birth__year__gte=request.GET["min_year"])

        if request.GET.get("max_year"):
            qs = qs.filter(date_of_birth__year__lte=request.GET["max_year"])

        if request.GET.get("score"):
            qs = qs.filter(voter_score=request.GET["score"])

        for field in ["v20state", "v21town", "v21primary", "v22general", "v23town"]:
            if request.GET.get(field) == "1":
                qs = qs.filter(**{field: True})

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voters = context["voters"]

        birth_years = [v.date_of_birth.year for v in voters]
        year_counts = Counter(birth_years)

        birth_graph = plot(
            [go.Bar(x=list(year_counts.keys()), y=list(year_counts.values()))],
            output_type="div"
        )

        parties = [v.party_affiliation for v in voters]
        party_counts = Counter(parties)

        party_graph = plot(
            [go.Pie(labels=list(party_counts.keys()), values=list(party_counts.values()))],
            output_type="div"
        )

        election_fields = ["v20state", "v21town", "v21primary", "v22general", "v23town"]
        election_labels = ["2020 State", "2021 Town", "2021 Primary", "2022 General", "2023 Town"]

        election_counts = [sum(getattr(v, field) for v in voters) for field in election_fields]

        election_graph = plot(
            [go.Bar(x=election_labels, y=election_counts)],
            output_type="div"
        )

        context["birth_graph"] = birth_graph
        context["party_graph"] = party_graph
        context["election_graph"] = election_graph

        context["years"] = range(1900, 2025)

        return context