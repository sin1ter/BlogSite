import random
from faker import Faker
from django.core.management.base import BaseCommand
from store_blogs.models import Blog, MyUser, Tag  

fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake blog data'

    def handle(self, *args, **kwargs):
        # Create some tags
        tags = [Tag.objects.create(name=fake.word()) for _ in range(10)]

        # Create a few users if you haven't already
        users = [MyUser.objects.create(username=fake.user_name(), email=fake.email()) for _ in range(5)]

        for _ in range(50):  # Generate 50 fake blog entries
            blog = Blog(
                title=fake.sentence(nb_words=6),
                content=fake.paragraph(nb_sentences=5),
                author=random.choice(users),
            )
            blog.save()
            # Add random tags to the blog
            blog.tags.set(random.sample(tags, k=random.randint(1, 3)))  # Select 1 to 3 random tags
            blog.save()

        self.stdout.write(self.style.SUCCESS('Successfully generated fake blog data'))
