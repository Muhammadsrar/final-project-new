# book/models.py (or icp/models.py)
from django.db import models
from user.models import CustomUser

class ICPProfile(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='icp_profiles')
    target_industries = models.TextField(help_text="Comma-separated list of industries")
    min_company_size = models.PositiveIntegerField(default=1)
    max_company_size = models.PositiveIntegerField(default=1000)
    target_roles = models.TextField(help_text="Comma-separated list of job roles or seniority")
    target_regions = models.TextField(blank=True, null=True, help_text="Comma-separated list of regions/countries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def industries_list(self):
        return [i.strip() for i in self.target_industries.split(',') if i.strip()]

    def roles_list(self):
        return [r.strip() for r in self.target_roles.split(',') if r.strip()]

    def regions_list(self):
        if self.target_regions:
            return [r.strip() for r in self.target_regions.split(',') if r.strip()]
        return []

    def __str__(self):
        return f"ICP Profile for {self.user.username}"