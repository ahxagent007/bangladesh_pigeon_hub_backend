from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.pigeons.models import Pigeon
from .models import PedigreeRecord
from .forms import PedigreeForm


def pedigree_index(request):
    """Show all public pedigrees, or user's own if logged in."""
    public_pedigrees = PedigreeRecord.objects.filter(
        is_public=True
    ).select_related('pigeon__breed', 'pigeon__owner', 'sire', 'dam')\
     .order_by('-created_at')

    my_pedigrees = None
    if request.user.is_authenticated:
        my_pedigrees = PedigreeRecord.objects.filter(
            pigeon__owner=request.user
        ).select_related('pigeon__breed', 'sire', 'dam')\
         .order_by('-created_at')

    return render(request, 'pedigrees/index.html', {
        'public_pedigrees': public_pedigrees,
        'my_pedigrees':     my_pedigrees,
    })


def pedigree_view(request, pigeon_id):
    pigeon = get_object_or_404(Pigeon, pk=pigeon_id)
    try:
        record = pigeon.pedigree
        tree   = record.get_ancestors(depth=3)
    except PedigreeRecord.DoesNotExist:
        record = None
        tree   = None
    can_edit = request.user.is_authenticated and pigeon.owner == request.user
    return render(request, 'pedigrees/tree.html', {
        'pigeon':   pigeon,
        'record':   record,
        'tree':     tree,
        'can_edit': can_edit,
    })


@login_required
def pedigree_edit(request, pigeon_id):
    pigeon = get_object_or_404(Pigeon, pk=pigeon_id, owner=request.user)
    try:
        record = pigeon.pedigree
    except PedigreeRecord.DoesNotExist:
        record = None

    if request.method == 'POST':
        form = PedigreeForm(request.POST, instance=record, pigeon=pigeon)
        if form.is_valid():
            pedigree         = form.save(commit=False)
            pedigree.pigeon  = pigeon
            pedigree.save()
            messages.success(request, 'Pedigree updated!')
            return redirect('pedigree-view', pigeon_id=pigeon_id)
    else:
        form = PedigreeForm(instance=record, pigeon=pigeon)

    return render(request, 'pedigrees/edit.html', {
        'pigeon': pigeon,
        'form':   form,
    })