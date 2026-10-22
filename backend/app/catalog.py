"""All wizard choices in one place: id -> label, short description, lucide icon name.

Served by GET /api/options (the frontend renders the wizard from it) and used by the
rule engine for display names. Keys must match the Literal types in app/schemas.py
(a test checks this).
"""

BUSINESS_TYPES = {
    "coffee_shop": {"label": "Coffee shop", "description": "Café, coffee bar or bakery with seating", "icon": "coffee"},
    "restaurant": {"label": "Restaurant", "description": "Restaurant, bistro or bar", "icon": "utensils"},
    "beauty_salon": {"label": "Beauty salon", "description": "Hair, nails, beauty or spa", "icon": "scissors"},
    "online_store": {"label": "Online store", "description": "You sell physical or digital products online", "icon": "shopping-bag"},
    "local_services": {"label": "Local services", "description": "Plumber, cleaner, tutor, repair and other local work", "icon": "wrench"},
    "freelancer": {"label": "Freelancer / Portfolio", "description": "Designer, developer, photographer, writer", "icon": "palette"},
    "consulting": {"label": "Consulting / Agency", "description": "Advisory, coaching or agency services", "icon": "briefcase"},
}

GOALS = {
    "bookings": {"label": "Get bookings", "description": "Customers reserve a table, appointment or call", "icon": "calendar-check"},
    "sell_online": {"label": "Sell online", "description": "Customers buy and pay on the website", "icon": "shopping-cart"},
    "leads": {"label": "Get leads / calls", "description": "Visitors send an enquiry or call you", "icon": "phone-call"},
    "brand": {"label": "Build brand awareness", "description": "People get to know and remember you", "icon": "megaphone"},
    "portfolio": {"label": "Show portfolio", "description": "Your work speaks for you", "icon": "images"},
}

AUDIENCES = {
    "local": {"label": "Local", "description": "Customers from your town or region", "icon": "map-pin"},
    "national": {"label": "National", "description": "Customers across the country", "icon": "flag"},
    "international": {"label": "International", "description": "Customers in several countries", "icon": "globe"},
}

LANGUAGES = {
    "en": {"label": "English"},
    "de": {"label": "German"},
    "fr": {"label": "French"},
    "es": {"label": "Spanish"},
    "it": {"label": "Italian"},
    "pl": {"label": "Polish"},
    "sk": {"label": "Slovak"},
    "cs": {"label": "Czech"},
    "uk": {"label": "Ukrainian"},
}

FEATURES = {
    "booking": {"label": "Online booking", "description": "Customers book a table, appointment or call", "icon": "calendar-days"},
    "payments": {"label": "Online payments", "description": "Take card and wallet payments on the site", "icon": "credit-card"},
    "blog": {"label": "Blog", "description": "Articles, news and tips", "icon": "newspaper"},
    "gallery": {"label": "Photo gallery", "description": "Show your space, products or work", "icon": "image"},
    "reviews": {"label": "Customer reviews", "description": "Testimonials and ratings", "icon": "star"},
    "map_hours": {"label": "Map & opening hours", "description": "Where you are and when you're open", "icon": "map"},
    "contact_form": {"label": "Contact form", "description": "Visitors send you a message", "icon": "message-square"},
    "multilingual": {"label": "Multiple languages", "description": "The site in more than one language", "icon": "languages"},
    "newsletter": {"label": "Newsletter signup", "description": "Collect emails to stay in touch", "icon": "mail"},
}

BUDGETS = {
    "starter": {"label": "Starter", "description": "Essentials only: launch fast, grow later", "icon": "sprout"},
    "standard": {"label": "Standard", "description": "A complete site for a growing business", "icon": "layers"},
    "advanced": {"label": "Advanced", "description": "Everything at once, built to scale", "icon": "rocket"},
}

TIMELINES = {
    "asap": {"label": "As soon as possible", "description": "Launch the essentials first", "icon": "zap"},
    "one_month": {"label": "Within a month", "description": "A planned, steady launch", "icon": "calendar"},
    "flexible": {"label": "Flexible", "description": "Quality over speed", "icon": "clock"},
}

SITE_TYPES = {
    "landing_page": "Landing page",
    "business_site": "Business website",
    "booking_site": "Booking website",
    "ecommerce": "Online store",
    "portfolio": "Portfolio",
}
