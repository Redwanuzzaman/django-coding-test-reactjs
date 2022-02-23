from django.views import generic

from product.models import Variant, Product
from django.views.generic import ListView


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    # There are issues in Product variants (React Issue)
    # The Create Product Page doesn't look appropriate as shown in the picture.
    # So skipping it for now
    # It can be made functional using CreateView

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ProductListView(ListView):
    paginate_by = 2
    model = Product
    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['product'] = True
        context['variants'] = Variant.objects.filter(active=True).all()
        return context

    def get_queryset(self):
        title = self.request.GET.get('title')
        created = self.request.GET.get('date')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        variant = self.request.GET.get('variant', '')

        context = super(ProductListView, self).get_queryset()
        if variant:
            var_type, value = variant.split('_')
            if var_type == 'Size':
                context = context.filter(product_variant_prices__product_variant_one__variant_title=value)
            elif var_type == 'Color':
                context = context.filter(product_variant_prices__product_variant_two__variant_title=value)
            elif var_type == 'Style':
                context = context.filter(product_variant_prices__product_variant_three__variant_title=value)
        if title:
            context = context.filter(title__icontains=title)
        if created:
            year, month, day = created.split('-')
            context = context.filter(created_at__year=year,
                                     created_at__month=month,
                                     created_at__day=day)
        if price_from and price_to:
            context = context.filter(product_variant_prices__price__gte=price_from, product_variant_prices__price__lte=price_to)
        elif price_from:
            context = context.filter(product_variant_prices__price__gte=price_from)

        elif price_to:
            context = context.filter(product_variant_prices__price__lte=price_to)
        return context
