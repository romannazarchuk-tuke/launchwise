"""LaunchWise rule engine: wizard answers -> website plan.

Transparent and deterministic: every decision comes from one of the tables below,
and every item in the output carries a short "why". Pure functions only (no DB, no HTTP).

Pipeline (see generate_plan):
  1. site type      = business base type, adjusted by goal (and budget for leads)
  2. features       = user picks + auto-recommendations; strongest trigger wins
  3. sitemap        = business pages + site-type/feature pages, budget decides launch vs later
  4. complexity     = site-type base + feature weights
  5. content ideas, SEO checklist, next steps, summary (all computed from the above)
"""

from app import catalog
from app.schemas import (
    Complexity,
    ContentIdeas,
    FeatureItem,
    NextStep,
    Page,
    PlanInput,
    PlanResult,
    SeoItem,
    SiteType,
)

ENGINE_VERSION = "1.3.0"

PRIORITY_RANK = {"must": 2, "nice": 1}

# --------------------------------------------------------------------------- #
# 1. Site type
# --------------------------------------------------------------------------- #

BASE_SITE_TYPE = {
    "coffee_shop": "business_site",
    "restaurant": "business_site",
    "beauty_salon": "booking_site",
    "online_store": "ecommerce",
    "local_services": "business_site",
    "freelancer": "portfolio",
    "consulting": "business_site",
}

BASE_SITE_TYPE_WHY = {
    "coffee_shop": "A coffee shop mainly needs to show its menu, location and opening hours. A clear business site does that best.",
    "restaurant": "A restaurant mainly needs to show its menu, location and atmosphere. A clear business site does that best.",
    "beauty_salon": "Salon clients expect to book online, so the site is built around booking an appointment.",
    "online_store": "You sell products, so the site has to be a shop: catalogue, product pages and checkout.",
    "local_services": "Local customers want to see your services, your area and how to reach you. A business site covers that.",
    "freelancer": "Clients hire freelancers based on their work, so the site puts your projects first.",
    "consulting": "Clients need to understand your services and trust your results. A business site with clear service pages does that.",
}

# Goals that change the site type (other goals keep the business base type).
GOAL_SITE_TYPE = {"sell_online": "ecommerce", "bookings": "booking_site", "portfolio": "portfolio"}

# What "booking" means for each business: used for page names and texts.
BOOKING_ACTION = {
    "coffee_shop": "reserve a table",
    "restaurant": "reserve a table",
    "beauty_salon": "book an appointment",
    "online_store": "book a consultation",
    "local_services": "book a visit",
    "freelancer": "book a call",
    "consulting": "book a call",
}
BOOKING_PAGE_NAME = {
    "coffee_shop": "Reserve a table",
    "restaurant": "Reserve a table",
    "beauty_salon": "Book an appointment",
    "online_store": "Book a consultation",
    "local_services": "Book a visit",
    "freelancer": "Book a call",
    "consulting": "Book a call",
}

# --------------------------------------------------------------------------- #
# 2. Features: recommendation triggers (feature, priority, why)
# --------------------------------------------------------------------------- #

FEATURE_DEFAULT_WHY = {
    "booking": "Lets customers book at any time without calling, which also saves you phone time.",
    "payments": "Customers can pay online, so a visit can turn into a sale right away.",
    "blog": "Regular articles bring search traffic and show your expertise.",
    "gallery": "Photos show your work or your space faster than any text.",
    "reviews": "Other customers' opinions build trust with new visitors.",
    "map_hours": "Visitors see where you are and when you're open at a glance.",
    "contact_form": "An easy way to get in touch, even outside working hours.",
    "multilingual": "Visitors can read the site in their own language.",
    "newsletter": "Lets interested visitors hear from you again, at almost no cost.",
}

GOAL_FEATURE = {
    "bookings": ("booking", "must", "Your main goal is bookings, so customers should be able to book online without calling."),
    "sell_online": ("payments", "must", "You want to sell online, so customers must be able to pay on the site."),
    "leads": ("contact_form", "must", "Your goal is leads, and a short contact form is the simplest way to get them."),
    "portfolio": ("gallery", "must", "Your goal is showing your work, so a good gallery is the core of the site."),
    "brand": ("blog", "nice", "Articles give people a reason to find and share your brand."),
}

LOCAL_FEATURE = ("map_hours", "must", "Local customers mainly need to know where you are and whether you're open now.")

BUSINESS_FEATURES = {
    "coffee_shop": [
        ("map_hours", "must", "Most coffee-shop visitors search 'coffee near me' and just need your location and hours."),
        ("reviews", "nice", "New guests trust other guests. Showing your Google reviews builds that trust."),
        ("gallery", "nice", "Photos of the space and drinks sell the atmosphere better than text."),
    ],
    "restaurant": [
        ("map_hours", "must", "Guests check location and opening hours before anything else."),
        ("booking", "nice", "Many guests prefer to reserve a table online, especially for evenings and weekends."),
        ("gallery", "nice", "Food and interior photos are what make people choose a restaurant."),
        ("reviews", "nice", "Diners read reviews before they try a new place."),
    ],
    "beauty_salon": [
        ("booking", "must", "Clients expect to book a salon appointment online, at any time of day."),
        ("gallery", "must", "Clients choose a salon by its results. Before/after photos are your best argument."),
        ("reviews", "nice", "Reviews reduce the risk of trying a new salon."),
        ("map_hours", "nice", "Helps new clients find you and plan their visit."),
    ],
    "online_store": [
        ("payments", "must", "An online store needs online payments to work at all."),
        ("reviews", "nice", "Product reviews are one of the strongest reasons to buy online."),
        ("newsletter", "nice", "Email brings customers back for a second purchase at almost no cost."),
    ],
    "local_services": [
        ("contact_form", "must", "People who need a service want a quick quote. A form gets you leads even while you're on a job."),
        ("reviews", "must", "For local services, reviews are the main way new customers judge whether to trust you."),
        ("map_hours", "nice", "Shows the area you serve and when you can be reached."),
    ],
    "freelancer": [
        ("gallery", "must", "Clients hire freelancers based on previous work, so a portfolio gallery is essential."),
        ("contact_form", "must", "Make it easy for a potential client to send a project request."),
    ],
    "consulting": [
        ("contact_form", "must", "Consulting starts with a conversation, so make the first contact easy."),
        ("reviews", "nice", "Client testimonials make a consultant's claims believable."),
        ("blog", "nice", "Articles show your expertise and bring in clients through search."),
    ],
}

# --------------------------------------------------------------------------- #
# 3. Sitemap
# --------------------------------------------------------------------------- #

# Budget -> how many pages go live at launch (None = all). Required pages don't count.
LAUNCH_PAGE_LIMIT = {"starter": 4, "standard": 6, "advanced": None}

# Pages per business type, in priority order.
BUSINESS_PAGES = {
    "coffee_shop": ["home", "menu", "visit", "our-story", "events"],
    "restaurant": ["home", "menu", "visit", "about", "private-events"],
    "beauty_salon": ["home", "services-prices", "team", "visit"],
    "online_store": ["home", "shop", "product", "cart", "shipping", "about", "contact"],
    "local_services": ["home", "services", "service-area", "contact", "about"],
    "freelancer": ["home", "work", "about", "contact", "services-rates"],
    "consulting": ["home", "services", "case-studies", "about", "contact"],
}

# Pages a site type adds right after Home (if the business doesn't already have them).
SITE_TYPE_PAGES = {
    "ecommerce": ["shop", "product", "cart", "shipping"],
    "portfolio": ["work"],
}

# Pages that are always "launch" and don't count toward the budget limit.
ALWAYS_REQUIRED = {"legal"}
ECOMMERCE_REQUIRED = {"shipping"}

def required_pages(site_type: str) -> set[str]:
    """Pages that are always "launch" and never count toward page limits or the complexity bonus."""
    return ALWAYS_REQUIRED | (ECOMMERCE_REQUIRED if site_type == "ecommerce" else set())


LEGAL_WHY = "Required by GDPR as soon as the site collects personal data (bookings, contact forms)."

LANDING_HOME_SECTIONS = ["Header", "Hero", "Services", "Testimonials", "Contact form", "FAQ", "Footer"]

HOME_HIGHLIGHT = {
    "coffee_shop": "Menu highlights",
    "restaurant": "Signature dishes",
    "beauty_salon": "Popular treatments",
    "online_store": "Featured products",
    "local_services": "Services",
    "freelancer": "Selected work",
    "consulting": "Services",
}

# Sections a feature adds to the Home page (in this order, before CTA/Footer).
FEATURE_HOME_SECTIONS = {
    "booking": "Booking widget",
    "map_hours": "Map & hours",
    "reviews": "Testimonials",
    "contact_form": "Contact form",
    "newsletter": "Newsletter signup",
}

# Pages a feature adds (at the end of the list, before Legal).
FEATURE_PAGES = {"gallery": "gallery", "blog": "blog"}

# key -> (name, slug, sections, why). "home" sections and "booking" name are computed.
PAGE_LIBRARY = {
    "home": ("Home", "/", [], "First impression: in five seconds visitors should see what you offer and what to do next."),
    "menu": ("Menu", "/menu", ["Header", "Menu categories", "Prices", "Dietary info", "CTA", "Footer"],
             "The menu is the page people look for most. Keep it current and easy to read on a phone."),
    "visit": ("Visit us", "/visit", ["Header", "Map & hours", "Contact details", "Directions & parking", "Footer"],
              "Answers the top questions for a local place: where are you, and are you open?"),
    "our-story": ("Our story", "/our-story", ["Header", "Story", "Team photo", "Values", "CTA", "Footer"],
                  "People choose a local place they feel connected to. A short story builds that."),
    "events": ("Events", "/events", ["Header", "Upcoming events", "Recurring formats", "CTA", "Footer"],
               "Events give regulars a reason to come back and give you fresh things to share."),
    "about": ("About", "/about", ["Header", "Story", "Team", "Values", "CTA", "Footer"],
              "Shows the people behind the business. Trust matters before someone gets in touch."),
    "private-events": ("Private events", "/private-events",
                       ["Header", "Spaces & capacity", "Packages", "Gallery", "Enquiry form", "Footer"],
                       "Group bookings are high-value. A dedicated page lets organisers find the details and enquire."),
    "services-prices": ("Services & prices", "/services", ["Header", "Treatment list", "Prices & duration", "CTA", "Footer"],
                        "Clients want to know what you offer and what it costs before they book."),
    "team": ("Team", "/team", ["Header", "Team members", "Specialities", "CTA", "Footer"],
             "Clients often book a specific person, so show who does what."),
    "shop": ("Shop", "/shop", ["Header", "Category filters", "Product grid", "Footer"],
             "Lets visitors browse everything you sell, with filters to find things fast."),
    "product": ("Product page", "/product", ["Header", "Product gallery", "Price & variants", "Add to cart", "Description", "Reviews", "Footer"],
                "The template for every product. This is where buying decisions happen."),
    "cart": ("Cart & checkout", "/checkout", ["Header", "Cart summary", "Delivery options", "Payment", "Order confirmation", "Footer"],
             "A short, trustworthy checkout is the difference between a visit and a sale."),
    "shipping": ("Shipping & returns", "/shipping-returns", ["Header", "Delivery times & costs", "Returns policy", "FAQ", "Footer"],
                 "Online shops must state delivery and return terms. Clear terms also reduce abandoned carts."),
    "contact": ("Contact", "/contact", ["Header", "Contact form", "Contact details", "Map", "Footer"],
                "Makes it easy to reach you in the way the visitor prefers."),
    "services": ("Services", "/services", ["Header", "Service list", "Process", "Pricing guide", "CTA", "Footer"],
                 "Explains exactly what you do, so the right customers get in touch."),
    "service-area": ("Service area", "/service-area", ["Header", "Area map", "Towns & districts", "CTA", "Footer"],
                     "Tells visitors (and Google) where you work, which helps you appear in local searches."),
    "work": ("Work", "/work", ["Header", "Project grid", "Filters", "CTA", "Footer"],
             "Your projects are the proof. This is the page clients will judge you on."),
    "services-rates": ("Services & rates", "/services", ["Header", "Services", "Rates", "Process", "CTA", "Footer"],
                       "Clear rates filter out bad-fit enquiries and save you time."),
    "case-studies": ("Case studies", "/case-studies", ["Header", "Case study cards", "Results", "Client quotes", "CTA", "Footer"],
                     "Results from real clients are the strongest argument for hiring a consultant."),
    "booking": ("", "/book", ["Header", "Booking widget", "What to expect", "Cancellation policy", "FAQ", "Footer"], ""),
    "faq": ("FAQ", "/faq", ["Header", "Questions & answers", "Contact CTA", "Footer"],
            "Answers the questions people have before they buy or book, so fewer of them give up."),
    "gallery": ("Gallery", "/gallery", ["Header", "Photo grid", "CTA", "Footer"],
                "Photos show what you offer faster than text."),
    "blog": ("Blog", "/blog", ["Header", "Post list", "Categories", "Newsletter signup", "Footer"],
             "Useful articles bring search traffic and show your expertise over time."),
    "legal": ("Privacy & imprint", "/privacy", ["Header", "Privacy policy", "Imprint", "Cookie notice", "Footer"], LEGAL_WHY),
}

# --------------------------------------------------------------------------- #
# 4. Complexity
# --------------------------------------------------------------------------- #

SITE_TYPE_BASE_SCORE = {"landing_page": 1, "portfolio": 2, "business_site": 2, "booking_site": 3, "ecommerce": 5}
# Languages count once, through "multilingual" (+2), whatever the number of languages.
FEATURE_WEIGHT = {"payments": 2, "multilingual": 2, "booking": 1, "blog": 1, "newsletter": 1}
MANY_PAGES = 7  # this many launch pages or more (not counting required pages like Legal) adds +1
ESTIMATED_WEEKS = {1: "1", 2: "1", 3: "1–2", 4: "2–3", 5: "3–4", 6: "4–5", 7: "5–6", 8: "6–8", 9: "8–12", 10: "8–12"}

# --------------------------------------------------------------------------- #
# 5. Content ideas (business-specific first, then generic per page)
# --------------------------------------------------------------------------- #

BUSINESS_CONTENT = {
    ("coffee_shop", "home"): [
        "A hero photo of your best-selling drink, with one line on what makes your coffee different",
        "Today's opening hours right under the hero",
        "Three signature items with prices",
        "One clear button for the main action (reserve, order or visit)",
    ],
    ("restaurant", "home"): [
        "A hero photo of a signature dish, not a stock image",
        "Cuisine, price range and neighbourhood in one sentence",
        "This week's specials",
        "Opening hours and a 'Reserve' button visible without scrolling",
    ],
    ("beauty_salon", "home"): [
        "Before/after photos of your best work",
        "Your most booked treatments with prices",
        "A 'Book now' button visible without scrolling",
        "A short line about hygiene and the products you use",
    ],
    ("online_store", "home"): [
        "One clear sentence: what you sell and for whom",
        "Bestsellers and new arrivals",
        "Free-shipping threshold and returns promise in the top bar",
        "Trust signals: payment logos and number of reviews",
    ],
    ("local_services", "home"): [
        "A headline with your service and area, e.g. 'Emergency plumber in <your city>'",
        "A phone number that can be tapped on mobile",
        "Your most requested services",
        "Your response time or guarantee",
    ],
    ("freelancer", "home"): [
        "One line: what you do and for whom",
        "Your best few projects, not everything",
        "Logos or names of clients you've worked with",
        "A clear 'Hire me' button",
    ],
    ("consulting", "home"): [
        "The problem you solve, in your client's words",
        "Results with real numbers from a few clients",
        "How working with you looks, in three steps",
        "A 'Book a call' button",
    ],
    ("coffee_shop", "menu"): [
        "Group by Coffee / Tea / Food / Seasonal",
        "Mark vegan, gluten-free and lactose-free options",
        "Say where your beans come from and who roasts them",
        "Keep the menu as text, not a PDF photo. Google can read it and it works on phones",
    ],
    ("restaurant", "menu"): [
        "Group by starters, mains, desserts and drinks",
        "Mark allergens and vegetarian/vegan dishes",
        "A specials section you can update quickly",
        "Keep the menu as text, not a PDF photo. Google can read it and it works on phones",
    ],
    ("local_services", "services"): [
        "One block per service: what's included, typical price, time needed",
        "Photos from real jobs",
        "Certifications and insurance",
        "Emergency or same-day availability",
    ],
    ("consulting", "services"): [
        "Each service as problem → approach → outcome",
        "Who it's for (and who it's not for)",
        "Typical engagement length and starting price",
        "One client quote per service",
    ],
    ("coffee_shop", "booking"): [
        "Time slots and maximum group size",
        "Rules for large groups and private hire",
        "What happens after booking: confirmation by email or SMS",
        "A phone number for last-minute tables",
    ],
    ("restaurant", "booking"): [
        "Time slots and maximum group size",
        "Rules for large groups and private hire",
        "What happens after booking: confirmation by email or SMS",
        "A phone number for last-minute tables",
    ],
    ("beauty_salon", "booking"): [
        "Pick treatment → stylist → time, in that order",
        "Duration and price next to each option",
        "Cancellation policy in one sentence",
        "A reminder email or SMS the day before",
    ],
}

GENERIC_CONTENT = {
    "home": [
        "One sentence on what you do and for whom",
        "Your main offer, with a clear button",
        "Proof: reviews, clients or numbers",
        "How to reach you",
    ],
    "menu": ["Group dishes or drinks by category", "Prices for every item", "Mark dietary options", "Keep it as text, not a PDF"],
    "visit": [
        "An embedded map and a 'Get directions' link",
        "Today's opening hours highlighted, plus holiday hours",
        "How to get there: nearest stop, parking, bike racks",
        "Accessibility: step-free entrance, toilets",
    ],
    "our-story": [
        "How and why you started, in a few short paragraphs",
        "A real photo of you and your team",
        "What you care about: sourcing, community, craft",
        "An invitation to visit",
    ],
    "events": [
        "Upcoming events with date, time and price",
        "Recurring formats (tastings, workshops, live music)",
        "Photos from past events",
        "How to book the space privately",
    ],
    "about": [
        "Your story and why you do this work",
        "Real photos of the people",
        "Experience, qualifications or years in business",
        "What customers can expect when working with you",
    ],
    "private-events": [
        "Spaces with capacity and photos",
        "Sample packages with price per person",
        "A simple enquiry form: date, guests, budget",
        "Feedback from past organisers",
    ],
    "services-prices": [
        "Group treatments by category (hair, nails, skin)",
        "Price and duration for every treatment",
        "'From' prices where it depends on length or style",
        "A book button next to each treatment",
    ],
    "team": [
        "Photo and specialities for each person",
        "Experience and training",
        "Which treatments each person does",
        "A 'Book with …' button per person",
    ],
    "shop": [
        "Categories that match how customers think, not how your warehouse works",
        "Filters for price, size and colour",
        "Sort by bestsellers by default",
        "Clear stock status on product cards",
    ],
    "product": [
        "Several real photos, including the product in use",
        "Benefits first, specs second",
        "Delivery date and returns info next to the buy button",
        "Customer reviews, ideally with photos",
    ],
    "cart": [
        "Guest checkout, no forced account",
        "Show the total including shipping early",
        "The payment methods your customers use most",
        "An order confirmation email with tracking",
    ],
    "shipping": [
        "Delivery times and costs per country or region",
        "Your free-shipping threshold",
        "Returns window and how to start a return",
        "Who pays for return shipping",
    ],
    "contact": [
        "A form with only the fields you really need",
        "Phone, email and how fast you reply",
        "Address and map if you have a location",
        "Opening hours or availability",
    ],
    "services": [
        "One block per service: what's included and who it's for",
        "Typical price or starting price",
        "Your process in a few steps",
        "A call to action after each service",
    ],
    "service-area": [
        "The towns and districts you cover",
        "A map of your area",
        "Travel fee rules, if any",
        "Reviews from customers in each area",
    ],
    "work": [
        "Your best projects, newest first",
        "For each: the problem, your role and the result",
        "Filters by type of work",
        "Full case studies for your top projects",
    ],
    "services-rates": [
        "Packages with what's included",
        "Starting prices or day rate",
        "Your process in a few steps",
        "Typical timeline",
    ],
    "case-studies": [
        "Client, challenge, approach, result, in that order",
        "Concrete numbers: revenue, time saved, growth",
        "A quote from the client",
        "Client logos (with permission)",
    ],
    "booking": [
        "Show available times without requiring an account",
        "Explain what happens after booking (confirmation, reminder)",
        "Cancellation policy in one sentence",
        "A phone number for people who prefer to call",
    ],
    "faq": [
        "Collect the questions customers ask most by phone and email",
        "Short answers with links to details",
        "Group questions by topic",
        "End with a contact button",
    ],
    "gallery": [
        "Real photos, no stock images",
        "Albums by theme (space, products, events)",
        "Short captions saying what's shown",
        "Add new photos after each season or event",
    ],
    "blog": [
        "First posts based on questions customers actually ask",
        "One good post a month is enough to start",
        "End every post with a call to action",
        "Topics you know better than anyone in your niche",
    ],
}

# --------------------------------------------------------------------------- #
# 6. SEO checklist: (id, title, category, why)
# --------------------------------------------------------------------------- #

SEO_MIN, SEO_MAX = 10, 14

SEO_ALWAYS = [
    ("title_meta", "Unique title and meta description for every page", "basics",
     "They are what people see in Google results, and they decide whether someone clicks."),
    ("one_h1", "One clear H1 heading per page", "basics",
     "Tells visitors and search engines what the page is about."),
    ("clean_urls", "Short, descriptive URLs (e.g. /menu, not /page?id=3)", "basics",
     "Readable URLs are easier to share and help Google understand the page."),
    ("alt_text", "Alt text on all meaningful images", "basics",
     "Makes images accessible and lets them appear in image search."),
    ("https_speed", "HTTPS and fast loading on mobile", "technical",
     "Most visitors are on phones. Slow or insecure sites lose them and rank lower."),
    ("sitemap_gsc", "XML sitemap submitted in Google Search Console", "technical",
     "Helps Google find all your pages and shows you errors and search queries."),
]

LOCAL_KEYWORD_EXAMPLE = {
    "coffee_shop": "coffee shop",
    "restaurant": "restaurant",
    "beauty_salon": "beauty salon",
    "online_store": "shop",
    "local_services": "plumber",
    "freelancer": "web designer",
    "consulting": "business consultant",
}
LOCAL_SCHEMA_TYPE = {
    "coffee_shop": "CafeOrCoffeeShop",
    "restaurant": "Restaurant",
    "beauty_salon": "BeautySalon",
    "online_store": "Store",
    "local_services": "LocalBusiness",
    "freelancer": "ProfessionalService",
    "consulting": "ProfessionalService",
}

SEO_FILLERS = [
    ("open_graph", "Open Graph tags for good link previews", "basics",
     "Links shared on social media and in messengers look better and get more clicks."),
    ("analytics", "Privacy-friendly analytics", "technical", "You can only improve what you measure."),
    ("internal_links", "Link related pages to each other", "content",
     "Helps visitors and search engines move through your site."),
    ("custom_404", "A helpful 404 page with links to key pages", "technical",
     "Visitors who hit a broken link stay instead of leaving."),
]

# --------------------------------------------------------------------------- #
# 7. Next steps and summary texts
# --------------------------------------------------------------------------- #

COLLECT_CONTENT = {
    "coffee_shop": "Collect your menu with prices, good photos of drinks and the space, and your opening hours.",
    "restaurant": "Collect your menu with prices, photos of dishes and the interior, and your opening hours.",
    "beauty_salon": "Collect your treatment list with prices and durations, team photos and before/after photos.",
    "online_store": "Prepare photos, descriptions and prices for your first products, plus your shipping and return terms.",
    "local_services": "Write down your services with typical prices and the towns you cover, and collect photos of real jobs.",
    "freelancer": "Pick your best projects and write a few sentences on each: the problem, your role, the result.",
    "consulting": "Write up a few case studies with concrete results and get your clients' approval to publish them.",
}

BUSINESS_NOUN = {
    "coffee_shop": "coffee shop",
    "restaurant": "restaurant",
    "beauty_salon": "beauty salon",
    "online_store": "shop",
    "local_services": "business",
    "freelancer": "freelance business",
    "consulting": "consultancy",
}

NEAR_ME_SEARCH = {
    "coffee_shop": "coffee near me",
    "restaurant": "restaurant near me",
    "beauty_salon": "salon near me",
    "online_store": "shop near me",
    "local_services": "<your service> near me",
    "freelancer": "<your skill> near me",
    "consulting": "consultant near me",
}


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def _join(names: list[str]) -> str:
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def split_pages(sitemap: list[Page]) -> tuple[list[Page], list[Page], list[Page]]:
    """(launch pages, required pages, later pages). Required pages are never counted as launch pages."""
    launch = [p for p in sitemap if p.priority == "launch" and not p.required]
    required = [p for p in sitemap if p.required]
    later = [p for p in sitemap if p.priority == "later"]
    return launch, required, later


def launch_group_text(sitemap: list[Page]) -> str:
    """e.g. "4 pages + required Privacy & imprint" (the Launch group's label)."""
    launch, required, _ = split_pages(sitemap)
    text = _plural(len(launch), "page")
    return text + (f" + required {_join([p.name for p in required])}" if required else "")


def page_counts_text(sitemap: list[Page]) -> str:
    """The one way page counts are described everywhere (summary, export, website):
    "4 pages at launch + required Privacy & imprint, 4 later". The frontend builds the same text
    from the same `required` / `priority` flags (frontend/src/lib/pageCounts.ts)."""
    launch, required, later = split_pages(sitemap)
    text = f"{_plural(len(launch), 'page')} at launch"
    if required:
        text += f" + required {_join([p.name for p in required])}"
    if later:
        text += f", {len(later)} later"
    return text


def _with_article(phrase: str) -> str:
    return ("an " if phrase[0].lower() in "aeiou" else "a ") + phrase


# --------------------------------------------------------------------------- #
# Steps of the pipeline
# --------------------------------------------------------------------------- #

def pick_site_type(inp: PlanInput) -> SiteType:
    business = inp.business_type
    if business == "online_store":
        site_id, why = "ecommerce", BASE_SITE_TYPE_WHY[business]
    elif inp.goal in GOAL_SITE_TYPE:
        site_id = GOAL_SITE_TYPE[inp.goal]
        why = {
            "ecommerce": "Your main goal is selling online, so the site needs a shop, product pages and a checkout.",
            "booking_site": f"Your main goal is bookings, so the site is built around one action: letting customers {BOOKING_ACTION[business]}.",
            "portfolio": "Your main goal is showing your work, so the site leads with projects and keeps everything else short.",
        }[site_id]
    else:
        site_id, why = BASE_SITE_TYPE[business], BASE_SITE_TYPE_WHY[business]

    if inp.goal == "leads" and site_id == "business_site" and inp.budget == "starter":
        site_id = "landing_page"
        why = "You want leads on a starter budget, so one focused page with a clear call to action beats several thin pages."

    return SiteType(id=site_id, name=catalog.SITE_TYPES[site_id], why=why)


def pick_features(inp: PlanInput) -> list[FeatureItem]:
    # Triggers in order of strength (goal > languages > audience > business).
    triggers = [GOAL_FEATURE[inp.goal]]
    if len(inp.languages) > 1:
        triggers.append(("multilingual", "must",
                         f"You chose {len(inp.languages)} languages, so the site needs a language switcher and translated pages."))
    if inp.audience == "local":
        triggers.append(LOCAL_FEATURE)
    triggers += BUSINESS_FEATURES[inp.business_type]

    # Several triggers for the same feature: highest priority wins; on a tie the stronger (earlier) trigger.
    best: dict[str, tuple[str, str]] = {}
    for feature, priority, why in triggers:
        if feature not in best or PRIORITY_RANK[priority] > PRIORITY_RANK[best[feature][0]]:
            best[feature] = (priority, why)

    items = []
    for feature in inp.features:  # the user's own picks
        priority, why = best.get(feature, ("nice", FEATURE_DEFAULT_WHY[feature]))
        if feature == "multilingual" and len(inp.languages) == 1:
            priority = "nice"
            why = "You picked multiple languages but chose only one. Add a second language, or keep this for later."
        items.append(FeatureItem(id=feature, name=catalog.FEATURES[feature]["label"],
                                 priority=priority, recommended=False, why=why))
    for feature, (priority, why) in best.items():  # what the user missed
        if feature not in inp.features:
            items.append(FeatureItem(id=feature, name=catalog.FEATURES[feature]["label"],
                                     priority=priority, recommended=True, why=why))

    items.sort(key=lambda f: -PRIORITY_RANK[f.priority])  # stable: must first, order kept inside groups
    return items


def _is_active(feature: FeatureItem) -> bool:
    """Feature that is part of the build: the user picked it, or we recommend it as a must."""
    return not feature.recommended or feature.priority == "must"


def _home_sections(inp: PlanInput, site_type: str, active: set[str]) -> list[str]:
    if site_type == "landing_page":
        sections = LANDING_HOME_SECTIONS[:-1]  # without Footer
    else:
        sections = ["Header", "Hero", HOME_HIGHLIGHT[inp.business_type]]
    for feature, section in FEATURE_HOME_SECTIONS.items():
        if feature in active and section not in sections:
            sections.append(section)
    if site_type != "landing_page":
        sections.append("CTA")
    sections.append("Footer")
    if "multilingual" in active:
        sections[0] = "Header with language switcher"
    return sections


def _make_page(key: str, inp: PlanInput, priority: str, home_sections: list[str], required: bool = False) -> Page:
    name, slug, sections, why = PAGE_LIBRARY[key]
    if key == "home":
        sections = home_sections
    if key == "booking":
        name = BOOKING_PAGE_NAME[inp.business_type]
        why = f"A dedicated page for one action: letting customers {BOOKING_ACTION[inp.business_type]}. Fewer steps means more bookings."
    return Page(key=key, name=name, slug=slug, priority=priority, required=required, sections=list(sections), why=why)


def build_sitemap(inp: PlanInput, site_type: str, features: list[FeatureItem]) -> list[Page]:
    active = {f.id for f in features if _is_active(f)}
    optional = {f.id for f in features if not _is_active(f)}  # nice-to-have recommendations
    home_sections = _home_sections(inp, site_type, active)

    # Which pages exist, in priority order (earlier pages get the launch slots first):
    #   1. core: business pages, site-type pages, the booking page
    #   2. pages for features the user picked or we mark "must" (e.g. Gallery)
    #   3. extras the engine adds on its own (FAQ)
    #   4. pages for nice-to-have recommendations (always "later")
    core, feature_pages, engine_extras, nice_pages = [], [], [], []
    if site_type == "landing_page":
        core = ["home"]
    else:
        core = list(BUSINESS_PAGES[inp.business_type])
        core[1:1] = [p for p in SITE_TYPE_PAGES.get(site_type, []) if p not in core]  # right after Home
        if "booking" in active | optional:
            core.insert(min(2, len(core)), "booking")  # 3rd place: right after the first content page
        if site_type in ("ecommerce", "booking_site"):
            engine_extras.append("faq")
    if site_type == "landing_page" and "booking" in active | optional:
        (feature_pages if "booking" in active else nice_pages).append("booking")
    for feature, page in FEATURE_PAGES.items():
        if page in core or (page == "gallery" and "work" in core):
            continue  # already there (the Work page already is the gallery)
        if feature in active:
            feature_pages.append(page)
        elif feature in optional:
            nice_pages.append(page)

    required = required_pages(site_type)
    limit = LAUNCH_PAGE_LIMIT[inp.budget]

    pages, counted = [], 0
    for key in core + feature_pages + engine_extras + nice_pages:
        if key in required:
            priority = "launch"
        elif site_type == "landing_page":
            priority = "launch" if key == "home" else "later"  # landing = one page; extras only later
        elif key in nice_pages:
            priority = "later"  # nice-to-have features never block the launch
        elif limit is None or counted < limit:
            priority, counted = "launch", counted + 1
        else:
            priority = "later"
        pages.append(_make_page(key, inp, priority, home_sections, required=key in required))
    pages.append(_make_page("legal", inp, "launch", home_sections, required=True))

    # Launch pages first, keeping the order inside each group.
    return sorted(pages, key=lambda p: p.priority != "launch")


def score_complexity(site_type: SiteType, features: list[FeatureItem], sitemap: list[Page]) -> Complexity:
    base = SITE_TYPE_BASE_SCORE[site_type.id]
    parts = [f"{site_type.name} ({base})"]
    score = base
    for f in features:
        weight = FEATURE_WEIGHT.get(f.id, 0)
        if _is_active(f) and weight:
            score += weight
            parts.append(f"{f.name.lower()} (+{weight})")
    required = required_pages(site_type.id)
    launch_count = sum(p.priority == "launch" and p.key not in required for p in sitemap)
    if launch_count >= MANY_PAGES:
        score += 1
        parts.append(f"{launch_count} pages at launch (+1)")

    raw = score
    score = max(1, min(10, score))
    label = "Simple" if score <= 3 else "Moderate" if score <= 6 else "Complex"
    if len(parts) == 1:
        why = f"{parts[0]} with no complex features."
    else:
        why = " + ".join(parts) + (f" = {raw}, capped at 10." if raw > 10 else f" = {score}.")
    return Complexity(score=score, label=label, estimated_weeks=ESTIMATED_WEEKS[score], why=why)


def content_ideas(inp: PlanInput, sitemap: list[Page]) -> list[ContentIdeas]:
    result = []
    for page in sitemap:
        if page.priority != "launch" or page.key == "legal":
            continue
        ideas = BUSINESS_CONTENT.get((inp.business_type, page.key)) or GENERIC_CONTENT[page.key]
        result.append(ContentIdeas(page=page.name, ideas=list(ideas)))
    return result


def seo_checklist(inp: PlanInput, site_type: str, features: list[FeatureItem]) -> list[SeoItem]:
    in_plan = {f.id for f in features}
    items = list(SEO_ALWAYS)

    if inp.audience == "local":
        items += [
            ("google_business_profile", "Claim and complete your Google Business Profile", "local",
             "It powers your listing on Google Maps, which many people see before your website."),
            ("nap", "Same name, address and phone everywhere (NAP consistency)", "local",
             "Matching details across the web make Google trust your location data."),
            ("local_keywords",
             f"Use local keywords, e.g. \"{LOCAL_KEYWORD_EXAMPLE[inp.business_type]} in <your city>\"", "local",
             "People search with the city name. Using it helps you show up for those searches."),
            ("local_schema", f"Add {LOCAL_SCHEMA_TYPE[inp.business_type]} structured data", "local",
             "Gives Google your address, hours and type of business in a machine-readable format."),
        ]
        if "reviews" in in_plan:
            items.append(("google_reviews", "Ask happy customers for Google reviews", "local",
                          "Reviews improve your Maps ranking and convince new customers."))
    if len(inp.languages) > 1 or "multilingual" in in_plan:
        items += [
            ("hreflang", "hreflang tags linking each language version", "technical",
             "Shows each visitor the right language in Google and avoids duplicate-content issues."),
            ("translated_meta", "Translate titles, descriptions and URLs, not just the page text", "content",
             "People search in their own language. Untranslated titles won't match their searches."),
        ]
    if site_type == "ecommerce":
        items += [
            ("product_schema", "Product structured data (price, availability, reviews)", "technical",
             "Lets Google show price and stars in results, which increases clicks."),
            ("product_descriptions", "Unique product descriptions, not copied manufacturer text", "content",
             "Copied text competes with hundreds of other shops. Unique text can rank."),
            ("canonical_filters", "Canonical URLs for filtered and sorted pages", "technical",
             "Stops filter combinations from creating thousands of duplicate pages."),
        ]
    if inp.business_type in ("coffee_shop", "restaurant"):
        items.append(("menu_text", "Publish the menu as text, not a PDF or photo", "content",
                      "Google can read and rank text. It also loads faster and works on phones."))
    if "booking" in in_plan:
        items.append(("booking_indexable", "Describe how to book in normal page text, not only inside the widget",
                      "technical", "Booking widgets are often invisible to Google. Plain text about booking is not."))
    if "blog" in in_plan:
        items.append(("blog_topics", "Plan blog topics from questions customers really ask", "content",
                      "Answering real questions brings visitors who are close to buying."))
    if site_type == "portfolio":
        items.append(("case_study_titles", "Name projects by client industry and result", "content",
                      "'Online shop redesign for a bakery' matches searches. 'Project 7' doesn't."))

    for filler in SEO_FILLERS:
        if len(items) >= SEO_MIN:
            break
        items.append(filler)

    return [SeoItem(id=i, title=t, category=c, why=w) for i, t, c, w in items[:SEO_MAX]]


def next_steps(inp: PlanInput, site_type: str, features: list[FeatureItem], sitemap: list[Page]) -> list[NextStep]:
    active = {f.id for f in features if _is_active(f)}
    launch, required, later = split_pages(sitemap)
    launch_pages = "the launch page" if len(launch) == 1 else f"the {len(launch)} launch pages"
    plus_required = _join([p.name for p in required])

    steps = [NextStep(title=COLLECT_CONTENT[inp.business_type],
                      why="Missing content is the most common reason a website launch slips.")]

    if inp.timeline == "asap":
        if later:
            title = (f"Go live first with {launch_pages} ({_join([p.name for p in launch])}) plus {plus_required}, "
                     f"then add the {_plural(len(later), 'later page')}.")
        else:
            title = f"Go live with {launch_pages} plus {plus_required} as soon as the content is ready."
        why = "A small site that's live soon beats a perfect one months from now."
    elif inp.timeline == "one_month":
        title = f"Get the content ready first, then build {launch_pages} plus {plus_required}."
        why = "With a month, building on finished content avoids redesigns and delays."
    else:
        if later:
            title = (f"Build {launch_pages} plus {plus_required}, then add {later[0].name} "
                     f"before you start promoting the site.")
        else:
            title = f"Build {launch_pages} plus {plus_required}, then focus on SEO and content."
        why = "A flexible timeline lets you launch with a fuller site instead of rushing."
    steps.append(NextStep(title=title, why=why))

    setup = []
    if "booking" in active:
        setup.append(NextStep(title="Choose a booking tool and set your rules (time slots, group size, cancellations).",
                              why="Booking is the core of the site, so choose the tool before design starts."))
    if site_type == "ecommerce":
        setup.append(NextStep(title="Set up a payment provider and your shipping rates.",
                              why="Checkout can't be built or tested without them."))
    if inp.audience == "local":
        setup.append(NextStep(title="Claim or update your Google Business Profile with the same hours and a link to the site.",
                              why="Local customers often find you on Google Maps first."))
    if len(inp.languages) > 1:
        names = _join([catalog.LANGUAGES[lang]["label"] for lang in inp.languages])
        setup.append(NextStep(title=f"Arrange translations for {names}.",
                              why="Translations take time and should be ready when the build starts."))
    if not setup:
        setup.append(NextStep(title="Register your domain and set up a business email address.",
                              why="An email on your own domain looks more professional and builds trust."))
    steps += setup[:2]

    if site_type == "ecommerce":
        steps.append(NextStep(title="After launch, email past customers or followers with a launch offer.",
                              why="Your first sales and reviews will most likely come from people who already know you."))
    elif inp.audience == "local":
        steps.append(NextStep(title="After launch, ask regular customers for a Google review.",
                              why="Reviews are one of the strongest local ranking signals and convince new customers."))
    elif site_type == "portfolio":
        steps.append(NextStep(title="Share your best project on LinkedIn or in your community, with a link to the site.",
                              why="A portfolio only works if the right people see it."))
    else:
        steps.append(NextStep(title="A few weeks after launch, check Google Search Console for errors and first search queries.",
                              why="It shows what people search to find you, so you know what content to add next."))
    return steps


def write_summary(inp: PlanInput, site_type: SiteType, sitemap: list[Page]) -> str:
    business = inp.business_type
    subject = inp.business_name or f"Your {BUSINESS_NOUN[business]}"
    purpose = {
        "landing_page": "one focused page that turns visitors into enquiries",
        "business_site": "a clear, fast site that shows what you offer and how to reach you",
        "booking_site": f"a site whose main job is letting customers {BOOKING_ACTION[business]}",
        "ecommerce": "product pages, a smooth checkout and clear delivery terms",
        "portfolio": "a site that puts your best work first and makes it easy to hire you",
    }[site_type.id]
    launch, _, _ = split_pages(sitemap)

    text = f"{subject} needs {_with_article(site_type.name.lower())}: {purpose}. "
    text += f"The plan: {page_counts_text(sitemap)}. Start with {_join([p.name for p in launch])}. "
    text += {
        "local": (f"Your customers are local, so most visits will come from Google Maps and "
                  f"'{NEAR_ME_SEARCH[business]}' searches. Location, opening hours and reviews matter most."),
        "national": "You serve customers across the country, so clear pages for what you offer and good search rankings matter most.",
        "international": "Your audience is international, so clear language versions and fast loading everywhere matter most.",
    }[inp.audience]
    return text


def generate_plan(inp: PlanInput) -> PlanResult:
    site_type = pick_site_type(inp)
    features = pick_features(inp)
    sitemap = build_sitemap(inp, site_type.id, features)
    return PlanResult(
        summary=write_summary(inp, site_type, sitemap),
        site_type=site_type,
        complexity=score_complexity(site_type, features, sitemap),
        sitemap=sitemap,
        features=features,
        content_ideas=content_ideas(inp, sitemap),
        seo_checklist=seo_checklist(inp, site_type.id, features),
        next_steps=next_steps(inp, site_type.id, features, sitemap),
    )
