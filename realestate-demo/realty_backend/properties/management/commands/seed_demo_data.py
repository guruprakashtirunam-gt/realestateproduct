from django.core.management.base import BaseCommand
from django.utils.text import slugify
from properties.models import City, Property


CITIES = [
    ("Mumbai", "https://images.unsplash.com/photo-1567157577867-05ccb1388e66?auto=format&fit=crop&w=700&q=80"),
    ("Delhi NCR", "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=700&q=80"),
    ("Bangalore", "https://images.unsplash.com/photo-1580891536616-8ea0f8b3b6d8?auto=format&fit=crop&w=700&q=80"),
    ("Pune", "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=700&q=80"),
    ("Hyderabad", "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=700&q=80"),
    ("Chennai", "https://images.unsplash.com/photo-1602941525421-8f8b81d3edbb?auto=format&fit=crop&w=700&q=80"),
    ("Kolkata", "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=700&q=80"),
    ("Ahmedabad", "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=700&q=80"),
]

LISTINGS = [
    dict(name="Sea-View 3BHK Apartment", city="Mumbai", address="Bandra West, Mumbai",
         price=42000000, status="sale", property_type="Apartment", bedrooms=3, bathrooms=3, area_sqft=1850,
         image_url="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=80",
         description="A sea-facing 3BHK on the 14th floor with a wraparound balcony, modular kitchen, and "
                     "dedicated covered parking. Five minutes from Bandra-Worli Sea Link, in a RERA-registered "
                     "tower with 24x7 security and power backup."),
    dict(name="Independent Villa with Garden", city="Bangalore", address="Whitefield, Bangalore",
         price=28500000, status="sale", property_type="Villa", bedrooms=4, bathrooms=4, area_sqft=3200,
         image_url="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=900&q=80",
         description="A gated-community villa with a private garden, home office, and rooftop terrace. Walking "
                     "distance to ITPL tech park, with clubhouse access, a swimming pool, and dedicated staff "
                     "quarters on the ground floor."),
    dict(name="Modern 2BHK Flat", city="Delhi NCR", address="Sector 62, Noida",
         price=7800000, status="sale", property_type="Apartment", bedrooms=2, bathrooms=2, area_sqft=1150,
         image_url="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=900&q=80",
         description="A freshly renovated 2BHK in a well-maintained society with a metro station eight minutes "
                     "away. Includes a modular kitchen, wooden flooring in both bedrooms, and one covered "
                     "parking slot."),
    dict(name="Luxury Penthouse", city="Hyderabad", address="Banjara Hills, Hyderabad",
         price=56000000, status="new", property_type="Penthouse", bedrooms=4, bathrooms=5, area_sqft=4200,
         image_url="https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=900&q=80",
         description="A duplex penthouse with a private plunge pool, home theatre, and panoramic city views "
                     "from the terrace. Part of a newly launched tower with a sky lounge, gym, and dedicated "
                     "concierge desk."),
    dict(name="Furnished 1BHK for Rent", city="Bangalore", address="Koramangala, Bangalore",
         price=32000, status="rent", property_type="Apartment", bedrooms=1, bathrooms=1, area_sqft=650,
         image_url="https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?auto=format&fit=crop&w=900&q=80",
         description="A fully furnished 1BHK above a row of cafes, with AC in both rooms, a washing machine, "
                     "and high-speed broadband already installed. Ideal for working professionals; broker fee "
                     "waived for a 12-month lease."),
    dict(name="Row House with Backyard", city="Pune", address="Baner, Pune",
         price=16500000, status="sale", property_type="Independent House", bedrooms=3, bathrooms=3, area_sqft=2100,
         image_url="https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=900&q=80",
         description="A corner row house with a small private backyard, attached servant room, and two-wheeler "
                     "plus car parking. Close to Baner-Pashan Link Road, with schools and a hospital within 2 km."),
    dict(name="3BHK Apartment for Rent", city="Kolkata", address="Alipore, Kolkata",
         price=45000, status="rent", property_type="Apartment", bedrooms=3, bathrooms=2, area_sqft=1600,
         image_url="https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=900&q=80",
         description="A spacious 3BHK in a heritage-adjacent building with high ceilings and a semi-open "
                     "kitchen. Maintenance staff on-site, generator backup, and a small park directly across "
                     "the street."),
    dict(name="New Launch 2BHK", city="Hyderabad", address="Gachibowli, Hyderabad",
         price=9500000, status="new", property_type="Apartment", bedrooms=2, bathrooms=2, area_sqft=1280,
         image_url="https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=900&q=80",
         description="Pre-launch pricing on a 2BHK in a tower under construction near the Financial District, "
                     "with possession expected in 18 months. Includes a clubhouse, co-working lounge, and "
                     "children's play area."),
]


class Command(BaseCommand):
    help = "Seeds the database with the same demo cities/listings used in the original frontend mockup."

    def handle(self, *args, **options):
        city_objs = {}
        for name, image_url in CITIES:
            city, _ = City.objects.get_or_create(
                name=name, defaults={'slug': slugify(name), 'image_url': image_url}
            )
            city_objs[name] = city
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(city_objs)} cities."))

        created = 0
        for item in LISTINGS:
            city = city_objs[item.pop('city')]
            _, was_created = Property.objects.get_or_create(
                name=item['name'], city=city, defaults={**item}
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} new property listings."))
