from .models import Item, Shipment, ItemShipmentGroup
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .forms import PostForm


class IndexView(ListView):
    model = Item
    template_name = 'core/index.html'


class SingleView(DetailView):
    model = Item
    template_name = 'core/single.html'
    context_object_name = 'item'


class EditView(UpdateView):
    model = Item
    fields = '__all__'
    template_name = 'core/form.html'
    extra_context = {'submit_action': 'Edit'}

    def get_success_url(self, **kwargs):
        return reverse_lazy("core:save", args=(self.object.id,))


class AddView(CreateView):
    model = Item
    fields = '__all__'
    template_name = 'core/form.html'
    extra_context = {'submit_action': 'Add'}

    def get_success_url(self, **kwargs):
        return reverse_lazy("core:save", args=(self.object.id,))


class Delete(DeleteView):
    model = Item
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('core:index')
    template_name = 'core/confirm-delete.html'


def save(request, id):
    item = get_object_or_404(Item, pk=id)
    form = PostForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
    return redirect('core:index')


class CreateShipment(ListView):
    model = Item
    template_name = 'core/create-shipment.html'


def process_shipment(request):
    item_added = False
    for item in Item.objects.all().iterator():
        amt = request.POST[str(item.id)]
        if amt == '' or amt == '0':
            continue
        if int(amt) < 0:
            messages.error(request, 'Cannot have negative quantities.')
            return redirect('core:create-shipment')
        if int(amt) > item.quantity:
            messages.error(request, 'Attempted to add more items than available.')
            return redirect('core:create-shipment')
        item_added = True
    if not item_added:
        messages.error(request, 'No items added.')
        return redirect('core:create-shipment')

    shipment = Shipment.objects.create()
    for item in Item.objects.all().iterator():
        amt = request.POST[str(item.id)]
        if amt == '' or amt == '0':
            continue
        ItemShipmentGroup.objects.create(item=item, shipment=shipment, amount=amt).save()
        item.quantity -= int(amt)
        item.save()
    return HttpResponseRedirect(reverse('core:single-shipment', args=(shipment.id,)))


class ViewShipmentSingle(DetailView):
    model = Shipment
    template_name = 'core/single-shipment.html'
    context_object_name = 'shipment'


class ViewShipments(ListView):
    model = Shipment
    template_name = 'core/shipments.html'