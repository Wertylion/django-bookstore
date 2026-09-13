from decimal import Decimal

from shop.models import Book


class Cart:
    session_key = 'cart'

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.session_key)
        if cart is None:
            cart = self.session[self.session_key] = {}
        self.cart = cart

    def add(self, book, quantity=1, override_quantity=False):
        book_id = str(book.id)
        quantity = int(quantity)

        if book_id not in self.cart:
            self.cart[book_id] = {
                'quantity': 0,
                'price': str(book.price),
            }

        if override_quantity:
            self.cart[book_id]['quantity'] = quantity
        else:
            self.cart[book_id]['quantity'] += quantity

        if self.cart[book_id]['quantity'] <= 0:
            self.remove(book)
        else:
            self.save()

    def remove(self, book):
        book_id = str(book.id)
        if book_id in self.cart:
            del self.cart[book_id]
            self.save()

    def clear(self):
        self.session[self.session_key] = {}
        self.cart = self.session[self.session_key]
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        book_ids = self.cart.keys()
        books = Book.objects.filter(id__in=book_ids)
        cart = {
            book_id: item.copy()
            for book_id, item in self.cart.items()
        }

        for book in books:
            item = cart[str(book.id)]
            item['book'] = book
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )
