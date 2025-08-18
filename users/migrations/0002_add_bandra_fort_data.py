from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            """
            INSERT INTO users_city (name, description, image) 
            VALUES ('Mumbai', 'The city of dreams and home to Bollywood', NULL);
            
            INSERT INTO users_attraction (name, city_id, type, info, address, duration_minutes, rating, interest_tags, reviews)
            VALUES (
                'Bandra Fort',
                (SELECT id FROM users_city WHERE name = 'Mumbai'),
                'monument',
                'Also known as Castella de Aguada, Bandra Fort is a historic fort built by the Portuguese in 1640.',
                'Byramji Jeejeebhoy Road, Bandstand, Bandra West, Mumbai',
                120,
                4.3,
                'culture,history,architecture',
                'Beautiful historic fort with amazing sunset views'
            );
            """,
            "DELETE FROM users_attraction WHERE name = 'Bandra Fort'; DELETE FROM users_city WHERE name = 'Mumbai';"
        ),
    ] 