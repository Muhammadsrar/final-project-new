from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, render, redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ICPForm
from .models import ICPProfile

@login_required
def icp_config(request, profile_id=None):
    if request.method == "POST":
        form = ICPForm(request.POST)
        if form.is_valid():
            icp = form.save(commit=False)
            icp.user = request.user
            icp.save()
            messages.success(request, "ICP Profile saved successfully!")
            return redirect('icp_config')
        else:
            print("Form errors:", form.errors)
    else:
        form = ICPForm()

    return render(request, 'icp_config.html', {'form': form})


@login_required
def icp_list(request):
    profiles = ICPProfile.objects.all()
    return render(request, 'icp_list.html', {'all_icps': profiles})

@login_required
def icp_edit(request, profile_id):
    icp = get_object_or_404(ICPProfile, id=profile_id)

    # ALWAYS prepare icp_data
    icp_data = {
        'id': icp.id,
        'target_industries': icp.target_industries,
        'min_company_size': icp.min_company_size,
        'max_company_size': icp.max_company_size,
        'target_roles': icp.target_roles,
        'target_regions': icp.target_regions
    }

    if request.method == "POST":
        form = ICPForm(request.POST, instance=icp)
        if form.is_valid():
            form.save()
            messages.success(request, "ICP Profile updated successfully!")
            return redirect('icp_list')   # ✅ FIXED
        else:
            print("Form errors:", form.errors)

    return render(request, 'icp_edit.html', {
        'icp_data': icp_data,
        'profile_id': profile_id
    })
@login_required
def icp_delete(request, profile_id):
    icp = ICPProfile.objects.get(id=profile_id)
    icp.delete()
    messages.success(request, "ICP Profile deleted successfully!")
    return redirect('icp_list')