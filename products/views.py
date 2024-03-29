from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect, render
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView

from common.views import TitleMixin
from products.models import Basket, Product, ProductCategory


class IndexView(TitleMixin, TemplateView):

    template_name = 'products/index.html'
    title = 'UltraStore'


class ProductDetailView(View):

    def get(self, request, *args, **kwargs):
        context = {"product": Product.objects.get(id=kwargs["pk"])}
        if request.user.is_authenticated:
            baskets = Basket.objects.filter(user=request.user)
            context['products_in_baskets'] = [basket.product.id for basket in baskets]
        else:
            context['products_in_baskets'] = []
        return render(request, 'products/product_detail.html', context=context)


class ProductsListView(TitleMixin, ListView):

    paginate_by = 6
    model = Product
    template_name = 'products/products.html'
    title = 'UltraStore - Каталог'
    ordering = '-quantity'

    def get_queryset(self):
        queryset = super(ProductsListView, self).get_queryset()
        category_id = self.kwargs.get('category_id')
        return queryset.filter(category_id=category_id) if category_id else queryset

    def get_context_data(self, **kwargs):
        context = super(ProductsListView, self).get_context_data()
        categories = ProductCategory.objects.all()
        context['categories'] = categories
        category_id = self.kwargs.get('category_id')
        if self.request.user.is_authenticated:
            baskets = Basket.objects.filter(user=self.request.user)
            context['products_in_baskets'] = [basket.product.id for basket in baskets]
        else:
            context['products_in_baskets'] = []
        if category_id:
            context['current_category'] = categories.get(id=category_id)
        return context


@login_required
def basket_add(request, product_id):
    product = Product.objects.get(id=product_id)
    baskets = Basket.objects.filter(user=request.user, product=product)

    if not baskets.exists():
        Basket.objects.create(user=request.user, product=product, quantity=1)
    else:
        basket = baskets.first()
        basket.quantity += 1
        basket.save()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def basket_down(request, product_id):
    product = Product.objects.get(id=product_id)
    basket = Basket.objects.get(user=request.user, product=product)
    if basket.quantity > 1:
        basket.quantity -= 1
        basket.save()

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        basket.delete()

        return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def basket_remove(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])
